from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage
from models import CallbackQuery, StateContext, User

from keyboards.admin_main import admin_main_factory, AdminMainCallbackFilter

from pages.calculate import send_admin_send_settings
from pages.user import send_site_code
from pages.admin import (
    send_admin_main, send_admin_subs, send_admin_users,
    send_admin_params, send_admin_payment
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_main_factory.parse(call.data)
    type = callback_data.get('type', '')
    value = callback_data.get('value', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'users':
        await send_admin_users(bot, call.message, state)

    if type == 'params':
        await send_admin_params(bot, call.message, state)

    if type == 'payment':
        await send_admin_payment(bot, call.message, state)

    if type == 'site_code':
        await send_site_code(bot, call.message, state, user)

    if type == 'back':
        await send_admin_main(bot, call.message, state)

    if type == 'subs':
        await send_admin_subs(bot, call.message)

    if type == 'send_settings':
        await send_admin_send_settings(bot, call.message, state, user)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore # TODO - check
        lambda _: True, pass_bot=True,
        admin_main=admin_main_factory.filter()
    )
