import asyncio
import json
import logging
import telebot
from aiohttp import web

from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates

from config_global import CRYPTOPAY_URL, PROD, YOOKASSA_URL, flask_port, base_url
from config_logger import logger

from callbacks.calculate import send_after_first_try
from callbacks.stats import edit_channel_post, edit_live_info, send_vote, send_week_stats

from initialize import bot
from db import db
from models import LiveInfo, LiveStats, LiveWait, SentMessages
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

    await send_vote(bot, int(stat_id))
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


async def stats_post(request: web.Request):
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return web.Response(status=403)

    await send_week_stats(bot, is_new_week=True)

    return web.Response()


async def calc_post(request: web.Request):
    # access_token = db.get_access_token()
    # api_key = request.headers.get('tg-api-key')

    # if access_token is None or api_key is None or access_token != api_key:
    #     return Response(status=400)

    calc_id = request.query.get('calc_id')
    if calc_id is None or not calc_id.isnumeric():
        return web.Response(status=403)

    await edit_channel_post(bot, int(calc_id))

    return web.Response()


async def live_info(request: web.Request):
    logger.info(1)
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    logger.info(f'{access_token} {api_key}')
    if access_token is None or api_key is None or access_token != api_key:
        return web.Response(status=403)

    res = await request.json()

    messages = res.get('messages')
    data: list[dict] = res.get('data')
    wait: list[dict] = res.get('wait')
    canceled: list[dict] = res.get('canceled')

    live = (
        None if messages is None else SentMessages(**messages),
        [LiveInfo(**el) for el in data],
        [LiveWait(**el) for el in wait],
        [LiveWait(**el) for el in canceled],
        LiveStats(**res)
    )

    await edit_live_info(bot, live)

    return web.Response()


async def shutdown(app):
    logger.info('Shutting down: removing webhook')
    await bot.remove_webhook()
    logger.info('Shutting down: closing session')
    await bot.close_session()


async def setup():
    logger.info('Starting up: removing old webhook')
    await bot.remove_webhook()

    if PROD:
        logger.info('Starting up: setting webhook')
        await bot.set_webhook(f'https://profmarkets.ai{base_url}/AAA/')
        # await bot.set_webhook(f'https://369f-188-225-49-128.ngrok-free.app{base_url}/AAA/')

    app = web.Application()

    routes = [
        web.post(base_url + '/AAA/', handle),
        web.post(base_url + CRYPTOPAY_URL, cryptobot_updates),
        web.post(base_url + YOOKASSA_URL, yookassa_updates),
        web.post(base_url + '/stats_post', stats_post),
        web.post(base_url + '/live-info', live_info),
        web.get(base_url + '/icon.png', get_icon),
        web.get(base_url + '/manifest.json', get_ton_manifest),
        web.get(base_url + '/vote_timeout', vote_timeout),
        web.get(base_url + '/first_timeout', first_timeout),
        web.get(base_url + '/calc_post', calc_post),
    ]

    app.add_routes(routes)

    app.on_cleanup.append(shutdown)

    logging.basicConfig(level=logging.INFO)

    return app

run_thread(bot)

if __name__ == '__main__':
    if PROD:
        web.run_app(
            setup(),
            host='127.0.0.1',
            port=flask_port,
            access_log=None
        )
    else:
        asyncio.run(bot.polling(skip_pending=True))
