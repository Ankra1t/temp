from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import CallbackQuery

from keyboards.admin_main import admin_main_factory, AdminMainCallbackFilter

from pages.calculate import send_admin_send_settings
from pages.user import send_site_code
from pages.admin import (
    send_admin_main, send_admin_users, send_admin_fut_posts, send_admin_workers,
    send_admin_params, send_admin_payment, send_admin_tariffs
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_main_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'users':
        await send_admin_users(bot, call.message, user_id)

    if type == 'workers':
        await send_admin_workers(bot, call.message, user_id)

    if type == 'fut_posts':
        await send_admin_fut_posts(bot, call.message, user_id)

    if type == 'tariffs':
        await send_admin_tariffs(bot, call.message, user_id)

    if type == 'params':
        await send_admin_params(bot, call.message, user_id)

    if type == 'payment':
        await send_admin_payment(bot, call.message, user_id)

    if type == 'site_code':
        await send_site_code(bot, call.message, user_id)

    if type == 'back':
        await send_admin_main(bot, call.message, user_id)

    if type == 'send_settings':
        await send_admin_send_settings(bot, call.message, user_id)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore # TODO - check
        lambda _: True, pass_bot=True,
        admin_main=admin_main_factory.filter()
    )
