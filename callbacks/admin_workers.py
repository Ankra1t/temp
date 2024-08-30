from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from db import db

from common.utils import is_digit, set_state_data

from keyboards.admin_workers import (
    admin_workers_factory, AdminWorkersCallbackFilter,
    kb_admin_workers_back,
)

from states.admin_workers import AdminWorkersState
from pages.admin import (
    send_admin_main, send_admin_workers, send_admin_workers_admin,
    send_admin_workers_redactors, send_admin_workers_support
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot):
    data = admin_workers_factory.parse(call.data)

    type = data.get('type', '')
    id = int(data.get('id', 0)) if is_digit(data.get('id', '')) else 0
    role = int(data.get('role', -1)) if is_digit(data.get('role', '')) else -1

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        await send_admin_main(bot, call.message, user_id)

    if type == 'workers':
        await send_admin_workers(bot, call.message, user_id)

    if type == 'admins':
        await send_admin_workers_admin(bot, call.message, user_id)

    if type == 'redactors':
        await send_admin_workers_redactors(bot, call.message, user_id)

    if type == 'support':
        await send_admin_workers_support(bot, call.message, user_id)

    if type == 'workers_list':
        await bot.delete_state(user_id, chat_id)
        mas = db.get_all_workes()
        res = ''

        for i in range(0, len(mas)):
            show_role = ''
            if mas[i].role == 1:
                show_role = 'Гл.админ'
            elif mas[i].role == 2:
                show_role = 'Редактор'
            elif mas[i].role == 3:
                show_role = 'Тех. поддержка'

            name = f'| @{mas[i].username}' if mas[i].username else ''

            res += f'\nID: {mas[i].id} {name} | {show_role}'

        await bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=kb_admin_workers_back()
        )

    # Удаление/Добавление
    if type == 'delete' or type == 'add':
        if role == 1:
            text = 'Отправьте ID админа'
        else:
            text = 'Отправьте ID редактора'

        if type == 'add':
            state = AdminWorkersState.add_id
        else:
            state = AdminWorkersState.delete_id

        markup = kb_admin_workers_back(role)

        await bot.set_state(user_id, state, chat_id)

        await set_state_data(bot, user_id, chat_id, {'role': role})
        await bot.edit_message_text(text, chat_id, mes_id, reply_markup=markup)

    if type == 'add_yes':
        if db.get_worker_role(id) is not None:
            await bot.edit_message_text(
                f'Админ с ID: {id} - уже есть!',
                chat_id, mes_id
            )
        else:
            if role == 1:
                role_show = 'ADMIN'
            else:
                role_show = 'EDITOR'

            db.add_worker(id, role_show)
            await bot.edit_message_text('Успешно!', chat_id, mes_id)

    if type == 'delete_yes':
        if db.get_worker_role(id) is not None:
            db.del_worker(id)
            await bot.edit_message_text('Успешно!', chat_id, mes_id)
        else:
            await bot.edit_message_text(
                'Админа с таким ID не существует!',
                chat_id, mes_id
            )

    if type == 'add_no' or type == 'delete_no':
        await bot.edit_message_text('Отменено!', chat_id, mes_id)

    if '_yes' in type or '_no' in type:
        if role == 1:
            await send_admin_workers_admin(bot, call.message, user_id, True)
        elif role == 2:
            await send_admin_workers_redactors(bot, call.message, user_id, True)

    # Тех. поддержка
    if type == 'update_support':
        await bot.set_state(user_id, AdminWorkersState.update_support, chat_id)
        await bot.edit_message_text(
            'Отправьте id для тех. поддержки:',
            chat_id, mes_id,
            reply_markup=kb_admin_workers_back(3)
        )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminWorkersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore
        lambda _: True, pass_bot=True,
        admin_workers=admin_workers_factory.filter())
