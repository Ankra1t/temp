from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db

from .filter import main_factory, MainCallbackFilter
from ..utils import choose_first_calculate_step
from ..pages import send_settings, send_main, send_stats


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    if type == 'calc':
        u_base = db.get_calc_user_settings(user_db_id)
        market = u_base.market if (u_base is not None) else 'crypto'

        bot.delete_message(chat_id, mes_id)
        choose_first_calculate_step(bot, user_id, call.message, market)

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if type == 'settings':
        send_settings(bot, call.message, user_id)

    if type == 'stats':
        send_stats(bot, call.message, user_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter()
    )
