from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio.context import StateContext

from db import db
from models import Message

from common.utils import digit_accept

from states.admin_workers import AdminWorkersState
from keyboards.admin_workers import kb_admin_workers_confirm, kb_admin_workers_back
from pages.admin import send_admin_workers_support


async def handle_add_id(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    id = digit_accept(message, int)

    data = state.data()
    current_role = data.get('role', 2)

    if id is None:
        await bot.send_message(
            chat_id, 'Введите чисо:',
            reply_markup=kb_admin_workers_back(current_role)
        )
        return

    user = db.get_user_by_id(id)

    if user is None:
        await bot.send_message(
            chat_id, f'Пользователя с id <b>{id}</b> нет в базе.\nВведите другой id:',
            reply_markup=kb_admin_workers_back(current_role)
        )
        return

    await state.add_data(id=id)
    await state.delete()
    await bot.send_message(
        chat_id, f'Добавить @{user.tg_username} с id: <b>{id}</b>?',
        reply_markup=kb_admin_workers_confirm(id, current_role, 'add')
    )


async def handle_delete_id(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    id = digit_accept(message, int)

    data = state.data()
    current_role = data.get('role', 2)

    if id is None:
        await bot.send_message(
            chat_id, 'Введите чисо:',
            reply_markup=kb_admin_workers_back(current_role))
        return

    await state.delete()
    await bot.send_message(
        message.chat.id, f'Удалить <b>{id}</b>?',
        reply_markup=kb_admin_workers_confirm(
            id, current_role, action='delete'
        )
    )


async def handle_support_id(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    support_id = digit_accept(message, int)
    if support_id is None:
        await bot.send_message(
            chat_id, 'Введите id поддержки числом:'
        )
        return

    db.update_support(support_id)

    await state.delete()
    await send_admin_workers_support(bot, message, user_id, True)


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_add_id, state=AdminWorkersState.add_id)

    reg_mes(handle_delete_id, state=AdminWorkersState.delete_id)

    reg_mes(handle_support_id, state=AdminWorkersState.update_support)
