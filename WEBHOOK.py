import asyncio
import json
import logging
import telebot
from telebot.types import BotCommand
from aiohttp import web
from telebot.apihelper import ApiTelegramException

from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates

from NOTIFIER import notifier
from common.calculation import getStrValueCount
from common.utils import get_print_float
from config_global import BASE_HOST, CRYPTOPAY_URL, PROD, YOOKASSA_URL, flask_port, BASE_URL
from config_logger import logger

from callbacks.calculate import send_after_first_try

from initialize import bot
from db import db
from keyboards.stats import kb_calc_not
from models import AdminCalcNot, CalcChannelNotification, UserCalcNot
from registration import reg


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


async def del_notification(request: web.Request):
    res = await request.text()
    data = CalcChannelNotification.model_validate_json(res)

    logger.info(
        f"Attempting to delete notifications for calcId: {data.calcId}")

    for i in range(len(data.chIds)):
        try:
            logger.info(
                f"Deleting message {data.mesIds[i]} from chat {data.chIds[i]}")
            await bot.delete_message(data.chIds[i], int(data.mesIds[i]))
        except ApiTelegramException as e:
            error_msg = str(e)
            if "message to delete not found" in error_msg:
                logger.info(
                    f"Message {data.mesIds[i]} in chat {data.chIds[i]} was already deleted")
            elif "message can't be deleted" in error_msg:
                logger.warning(
                    f"Message {data.mesIds[i]} in chat {data.chIds[i]} cannot be deleted (possibly no permissions)")
            else:
                logger.error(
                    f"Telegram API error while deleting message {data.mesIds[i]} from chat {data.chIds[i]}: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error while deleting message {data.mesIds[i]} from chat {data.chIds[i]}: {e}")

    return web.Response()


async def user_not(request: web.Request):
    # access_token = db.get_access_token()
    # api_key = request.headers.get('tg-api-key')

    # if access_token is None or api_key is None or access_token != api_key:
    #     return web.Response(status=403)

    value = await request.text()

    if 'userIds' in value:
        data = AdminCalcNot.model_validate_json(value)

        deal = f'⚡️ {data.calc.tool}'
        result = ''

        if data.calc.status == 'CANCEL':
            result = f'<b>отменена!</b>'
        elif data.calc.status == 'DEAL':
            result = f'<b>в сделке!</b>\nВошел по {get_print_float(data.calc.openPrice)} USDT'
        elif data.calc.status == 'FINISH':
            valueCount = (data.calc.profit or 0) / data.calc.riskValue
            result = f'<b>завершена!</b>\nРезультат {getStrValueCount(valueCount)}'

        for el in data.userIds:
            try:
                await bot.send_message(
                    el, deal + f' пользователя {data.userName} ' + result
                )
            except:
                pass

        try:
            stats = '\n\n<b>Всего за текущий месяц:</b>'
            stats += f'\n{data.userStats.longCount + data.userStats.shortCount} сделок ({data.userStats.longCount} лонг / {data.userStats.shortCount} шорт)'
            stats += f'\nОбщий результат: {getStrValueCount(data.userStats.profitCount)}'

            await bot.send_message(
                data.userTgId, deal + ' ' + result + stats,
                reply_markup=kb_calc_not('ru', data.calc.id)
            )
        except:
            pass

    else:
        data = UserCalcNot.model_validate_json(value)

        tool = f'<a href="https://t.me/c/{str(data.chId).replace("-100", "")}/{data.mesId}">{data.tool}</a>'

        user = db.get_user_by_id(data.userId)

        if not user:
            return web.Response()

        if data.type == 'cancel':
            await bot.send_message(
                user.tg_id, f'⚡️ Сделка {tool} отменена!'
            )
        elif data.trStop is not None:
            tr_info = 'стоп передвинут '
            if data.trStop[0] == 'breakeven':
                tr_info += f'к <b>безубытку</b> ({get_print_float(data.trStop[1])})'
            else:
                tr_info += f'c {get_print_float(data.trStop[0])} к {get_print_float(data.trStop[1])}'

            await bot.send_message(
                user.tg_id, f'⚡️ По сделке {tool} {tr_info}!'
            )

    return web.Response()


async def site_visited(request: web.Request):
    value = await request.json()

    await notifier.send_site_visited(value.get('userId'))

    return web.Response()


async def user_code(request: web.Request):
    tgId: int | None = (await request.json()).get('tgId')
    code: str | None = (await request.json()).get('code')

    if not tgId or not code:
        return web.Response(status=400)

    await bot.send_message(
        tgId, f'Ваш код доступа <span class="tg-spoiler">{code}</span>'
    )
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
    await bot.set_webhook(
        f'{BASE_HOST}{BASE_URL}/AAA/',
        allowed_updates=[
            "message", "edited_message", "channel_post", "edited_channel_post", "inline_query", "chosen_inline_result",
            "callback_query", "shipping_query", "pre_checkout_query", "my_chat_member", "chat_member",
                              "chat_join_request", "chat_boost", "removed_chat_boost",
                              "business_connection", "business_message", "edited_business_message", "deleted_business_messages"
        ],
        drop_pending_updates=True
    )

    commands = [
        ('start', 'restart'),
        ('menu', 'menu'),
        ('calculator', 'calc'),
        ('settings', 'settings'),
        ('referral', 'partner'),
    ]

    await bot.set_my_commands([
        BotCommand(
            command=el[0],
            description=el[1],
        ) for el in commands
    ])

    reg(bot)

    app = web.Application()

    routes = [
        web.post(BASE_URL + '/AAA/', handle),
        web.post(BASE_URL + CRYPTOPAY_URL, cryptobot_updates),
        web.post(BASE_URL + YOOKASSA_URL, yookassa_updates),
        web.post(BASE_URL + '/user-not', user_not),
        web.post(BASE_URL + '/site-visited', site_visited),
        web.post(BASE_URL + '/user-code', user_code),
        web.post(BASE_URL + '/del_notification', del_notification),
        web.get(BASE_URL + '/icon.png', get_icon),
        web.get(BASE_URL + '/manifest.json', get_ton_manifest),
        web.get(BASE_URL + '/first_timeout', first_timeout),
    ]

    app.add_routes(routes)
    app.on_cleanup.append(shutdown)
    return app

if __name__ == '__main__':
    web.run_app(
        setup(),
        host='127.0.0.1',
        port=flask_port,
        access_log=None
    )
