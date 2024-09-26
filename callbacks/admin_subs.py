from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import CallbackQuery, StateContext, User

from keyboards.admin_subs import (
    admin_subs_factory, AdminSubsCallbackFilter, kb_admin_subs_choose_type, kb_admin_subs_choose_user,
)
from pages.admin import send_admin_main, send_admin_subs
from states.admin_tariff import AdminSubsState


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_subs_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'back':
        await send_admin_subs(bot, call.message)

    if type == 'main':
        await send_admin_main(bot, call.message, state)

    if type == 'set':
        await bot.edit_message_text(
            'Выберите подписку для пользователя',
            chat_id, mes_id,
            reply_markup=kb_admin_subs_choose_type()
        )

    if 'set+' in type:
        _, value = type.split('+')

        await bot.edit_message_text(
            'Введите тг id или ник пользователя',
            chat_id, mes_id,
            reply_markup=kb_admin_subs_choose_user()
        )
        await state.set(AdminSubsState.user_id_name)
        await state.add_data(
            sub_type=value
        )

    if type == 'list':
        msg = ''
        await bot.edit_message_text(
            msg, chat_id, mes_id,
        )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminSubsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        admin_subs=admin_subs_factory.filter())
