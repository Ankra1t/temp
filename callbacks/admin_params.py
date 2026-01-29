from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import CallbackQuery, StateContext, User

from keyboards.admin_params import admin_params_factory, AdminParamsCallbackFilter, kb_calculator

from pages.admin import send_admin_main, send_admin_params


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_params_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        await send_admin_main(bot, call.message, state)

    if type == 'go_params':
        await send_admin_params(bot, call.message, state)

    if type == 'calculator':
        await bot.edit_message_text(
            f'<b>Калькулятор расчета рисков</b>\nТех. поддержка: @calcsup',
            chat_id, mes_id,
            reply_markup=kb_calculator()
        )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminParamsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        admin_params=admin_params_factory.filter())
