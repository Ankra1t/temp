from telebot import TeleBot
from telebot.types import CallbackQuery

from MAIN.callbacks.user.pages import send_site_code

from .filter import admin_main_factory, AdminMainCallbackFilter
from ..pages import (
    send_admin_users, send_admin_fut_posts, send_admin_workers,
    send_admin_params, send_admin_payment, send_admin_tariffs
)


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = admin_main_factory.parse(call.data)
    type = data.get('type', '')

    user_id = call.from_user.id

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

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_main=admin_main_factory.filter()
    )
