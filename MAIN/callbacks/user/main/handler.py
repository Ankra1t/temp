from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.callbacks.utils import send_calc_start
from config_logger import logger
from AuthRoles import check_registrate
from MAIN.callbacks import (
    send_user_education, send_user_account, send_site_code,
    send_admin_main, send_user_main
)
from MAIN.common.utils import send_in_development

from pages.calculate import send_main

from .filter import user_main_factory, UserMainCallbackFilter

def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_main_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    logger.info(f'callback "user_main_factory" user_tg_id={user_id} type={type}')

    role = check_registrate(user_id) or 0

    if type == 'main':
        if role == 1:
            send_admin_main(bot, call.message, user_id)
        else:
            send_user_main(bot, call.message, user_id)

    if type == 'education':
        send_user_education(bot, call.message, user_id)

    if type == 'account':
        send_user_account(bot, call.message, user_id)

    if type == 'calculator':
        send_main(call.message, bot, user_id)

    if type == 'try':
        send_calc_start(bot, call.message, user_id, is_try=True)

    if type == 'signals':
        send_in_development(bot, call.message)

    if 'site' in type:
        is_reset = 'reset' in type
        send_site_code(bot, call.message, user_id, False, is_reset)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_main=user_main_factory.filter()
    )
