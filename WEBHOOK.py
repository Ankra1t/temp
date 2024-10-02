import asyncio
import json
import logging
import telebot
from aiohttp import web

from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates
from CHANNEL.channel_post import channel_post

from config_global import BASE_HOST, CRYPTOPAY_URL, PROD, YOOKASSA_URL, flask_port, BASE_URL
from config_logger import logger

from callbacks.calculate import send_after_first_try

from initialize import bot
from db import db
from models import Calculation, Live
from registration import reg
from thread_tasks import run_thread


async def handle(request: web.Request):
    if request.headers.get('content-type') == 'application/json':
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)

        if update is None:
            return web.Response(status=403)

        asyncio.ensure_future(bot.process_new_updates([update]))
        return web.Response()
    else:
        return web.Response(status=403)


async def cryptobot_updates(request: web.Request):
    return await cryptoPay_payment_updates(bot, request)


async def yookassa_updates(request: web.Request):
    return await yooKassa_payment_updates(bot, request)


async def get_icon(request: web.Request):
    return web.FileResponse(
        path='src/img/icon.png',
    )


async def get_ton_manifest(request: web.Request):
    return web.Response(
        body=json.dumps({
            "url": "https://github.com/XaBbl4/pytonconnect",
            "name": "Calc",
            "iconUrl": "https://profmarkets.ai/_prodbots/icon.png",
        }),
    )


async def vote_timeout(request: web.Request):
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return web.Response(status=403)

    stat_id = request.query.get('stat_id')
    if stat_id is None or not stat_id.isnumeric():
        return web.Response(status=403)

    await channel_post.send_vote(int(stat_id))
    return web.Response()


async def first_timeout(request: web.Request):
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return web.Response(status=403)

    user_id = request.query.get('user_id')
    if user_id is None or not user_id.isnumeric():
        return web.Response(status=403)

    try:
        await send_after_first_try(bot, int(user_id))
    except:
        return web.Response(status=403)

    return web.Response()


async def live_info(request: web.Request):
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return web.Response(status=403)

    live = Live.model_validate_json(await request.text())

    await channel_post.send_live(live)

    return web.Response()


async def active_calc(request: web.Request):
    # access_token = db.get_access_token()
    # api_key = request.headers.get('tg-api-key')

    # if access_token is None or api_key is None or access_token != api_key:
    #     return web.Response(status=403)

    res = await request.text()
    res_json = json.loads(res)
    calc = Calculation.model_validate_json(res)

    await channel_post.send_calc(calc, None, res_json.get('indexPrice'), False)

    return web.Response()


async def shutdown(app):
    logger.info('Shutting down: removing webhook')
    await bot.remove_webhook()
    logger.info('Shutting down: closing session')
    await bot.close_session()


async def setup():
    if PROD:
        logging.basicConfig(level=logging.INFO)

    logger.info('Starting up: removing old webhook')
    await bot.remove_webhook()

    logger.info('Starting up: setting webhook')
    await bot.set_webhook(f'{BASE_HOST}{BASE_URL}/AAA/')

    reg(bot)

    app = web.Application()

    routes = [
        web.post(BASE_URL + '/AAA/', handle),
        web.post(BASE_URL + CRYPTOPAY_URL, cryptobot_updates),
        web.post(BASE_URL + YOOKASSA_URL, yookassa_updates),
        web.post(BASE_URL + '/live-info', live_info),
        web.post(BASE_URL + '/active-calc', active_calc),
        web.get(BASE_URL + '/icon.png', get_icon),
        web.get(BASE_URL + '/manifest.json', get_ton_manifest),
        web.get(BASE_URL + '/vote_timeout', vote_timeout),
        web.get(BASE_URL + '/first_timeout', first_timeout),
    ]

    app.add_routes(routes)

    app.on_cleanup.append(shutdown)

    return app

run_thread(bot)

if __name__ == '__main__':
    web.run_app(
        setup(),
        host='127.0.0.1',
        port=flask_port,
        access_log=None
    )
