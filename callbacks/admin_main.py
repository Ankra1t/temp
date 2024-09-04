from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import CallbackQuery, User

from keyboards.admin_main import admin_main_factory, AdminMainCallbackFilter

from pages.calculate import send_admin_send_settings
from pages.user import send_site_code
from pages.admin import (
    send_admin_main, send_admin_users, send_admin_fut_posts, send_admin_workers,
    send_admin_params, send_admin_payment, send_admin_tariffs
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_main_factory.parse(call.data)
    type = callback_data.get('type', '')

    if type == 'users':
        await send_admin_users(bot, call.message, user.tgId)

    if type == 'workers':
        await send_admin_workers(bot, call.message, user.tgId)

    if type == 'fut_posts':
        await send_admin_fut_posts(bot, call.message, user.tgId)

    if type == 'tariffs':
        await send_admin_tariffs(bot, call.message, user.tgId)

    if type == 'params':
        await send_admin_params(bot, call.message, user.tgId)

    if type == 'payment':
        await send_admin_payment(bot, call.message, user.tgId)

    if type == 'site_code':
        await send_site_code(bot, call.message, user.tgId)

    if type == 'back':
        await send_admin_main(bot, call.message, user.tgId)

    if type == 'send_settings':
        await send_admin_send_settings(bot, call.message, user.tgId)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore # TODO - check
        lambda _: True, pass_bot=True,
        admin_main=admin_main_factory.filter()
    )
