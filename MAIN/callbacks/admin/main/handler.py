from telebot import TeleBot
from telebot.types import CallbackQuery

from MAIN.callbacks.admin.main.keyboards import kb_channel_stat
from MAIN.callbacks.user.pages import send_site_code
from config_global import EN_CHANNEL_ID, RU_CHANNEL_ID
from data.data import liteDb
from db import db
from models import Calculation
from CALCULATE.common.messages import trading_styles_translates
from Classes import text_editor

from .filter import admin_main_factory, AdminMainCallbackFilter
from ..pages import (
    send_admin_main, send_admin_users, send_admin_fut_posts, send_admin_workers,
    send_admin_params, send_admin_payment, send_admin_tariffs
)


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = admin_main_factory.parse(call.data)
    type = data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'users':
        send_admin_users(bot, call.message, user_id)

    if type == 'workers':
        send_admin_workers(bot, call.message, user_id)

    if type == 'fut_posts':
        send_admin_fut_posts(bot, call.message, user_id)

    if type == 'tariffs':
        send_admin_tariffs(bot, call.message, user_id)

    if type == 'params':
        send_admin_params(bot, call.message, user_id)

    if type == 'payment':
        send_admin_payment(bot, call.message, user_id)

    if type == 'site_code':
        send_site_code(bot, call.message, user_id)

    if type == 'back':
        send_admin_main(bot, call.message, user_id)

    if 'ch_stats' in type:
        send_datas = liteDb.getAllSendCalcs()

        stats: list[Calculation] = []
        count_short = 0
        count_long = 0
        tools = {}
        styles = {}

        for el in send_datas:
            stat = db.get_calculation(el.id, True)
            if stat is None:
                continue

            if stat.open_price > stat.stop_loss:
                count_long += 1
            else:
                count_short += 1

            tool = stat.tool
            if stat.forex_info is not None:
                tool = '/'.join(stat.forex_info.pair)

            tool = (tool or '').replace('/USDT', '')

            if tool in tools.keys():
                tools[tool or ''] += 1
            else:
                tools[tool or ''] = 1

            if stat.trading_style in styles.keys():
                styles[stat.trading_style] += 1
            else:
                styles[stat.trading_style] = 1

            stats.append(stat)

        max_tools: tuple[str, str] | None = None
        max_style: str = ''

        for el in tools.keys():
            if max_tools is None:
                max_tools = (el, '')
            elif max_tools[1] == '':
                max_tools = (max_tools[0], el)
            else:
                first_tool = max_tools[0]

                if tools[first_tool] < tools[el]:
                    max_tools = (first_tool, el)
                if tools[max_tools[1]] < tools[first_tool]:
                    max_tools = (max_tools[1], first_tool)

        for el in styles.keys():
            if max_style == '':
                max_style = el
            else:
                if styles[max_style] < styles[el]:
                    max_style = el

        count_all = len(stats)

        channels = (RU_CHANNEL_ID, EN_CHANNEL_ID)

        if 'send' not in type:
            text = f""" - {count_all} сделок
- {count_short} в шорт
- {count_long} в лонг

Чаще всего торговал: <b>{' '.join(max_tools or [])}</b>
Чаще всего: <b>{max_style}</b>"""

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_channel_stat()
            )
        else:
            for i, CHANNEL_ID in enumerate(channels):
                lang = 'ru' if i == 0 else 'en'

                if lang == 'ru':
                    text = f""" - {count_all} сделок
- {count_short} в шорт
- {count_long} в лонг

Чаще всего торговал: <b>{' '.join(max_tools or [])}</b>
Чаще всего: <b>{max_style}</b>"""
                else:
                    result = trading_styles_translates.get(max_style)

                    if result is None:
                        try:
                            result = str(
                                text_editor.translator.translate(
                                    max_style, 'en', 'ru'
                                ).text
                            )
                        except:
                            result = max_style
                    text = f""" - {count_all} deals
- {count_short} short
- {count_long} long

Most often traded: <b>{' '.join(max_tools or [])}</b>
More often: <b>{result}</b>"""
            bot.send_message(
                CHANNEL_ID, text
            )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_main=admin_main_factory.filter()
    )
