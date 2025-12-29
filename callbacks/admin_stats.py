from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import CallbackQuery, StateContext, User

from pages.admin import send_admin_main, send_admin_payment

from keyboards.admin_stats import (
    admin_statistics_factory, AdminStatisticsCallbackFilter,
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_statistics_factory.parse(call.data)
    type = callback_data.get('type', '')

    if type == 'go_main':
        await send_admin_main(bot, call.message, state)

    if type == 'go_payment':
        await send_admin_payment(bot, call.message, state)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminStatisticsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        admin_params=admin_statistics_factory.filter())
