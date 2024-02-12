from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new

from common.utils import is_digit, set_state_data
from MAIN.states import AdminWorkersState

from .filter import admin_workers_factory, AdminWorkersCallbackFilter
from .keyboards import kb_admin_workers_actions, kb_admin_workers_back
from ..pages import send_admin_workers, send_admin_workers_admin, send_admin_workers_redactors, send_admin_workers_support


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = admin_workers_factory.parse(call.data)

    type = data.get('type', '')
    id = int(data.get('id', 0)) if is_digit(data.get('id', '')) else 0
    role = int(data.get('role', -1)) if is_digit(data.get('role', '')) else -1

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'workers':
        send_admin_workers(bot, call.message, user_id)

    if type == 'admins':
        send_admin_workers_admin(bot, call.message, user_id)

    if type == 'redactors':
        send_admin_workers_redactors(bot, call.message, user_id)

    if type == 'support':
        send_admin_workers_support(bot, call.message, user_id)

    if type == 'workers_list':
        bot.delete_state(user_id, chat_id)
        mas = db_new.get_all_workes()
        res = ''

        for i in range(0, len(mas)):
            show_role = ''
            if mas[i].role == 1:
                show_role = 'Гл.админ'
            elif mas[i].role == 2:
                show_role = 'Редактор'
            elif mas[i].role == 3:
                show_role = 'Тех.поддержка'

            name = f'| @{mas[i].username}' if mas[i].username else ''

            res += f'\nID: {mas[i].id} {name} | {show_role}'

        bot.edit_message_text(
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

        bot.set_state(user_id, state, chat_id)
        set_state_data(bot, user_id, chat_id, {'role': role})
        bot.edit_message_text(text, chat_id, mes_id, reply_markup=markup)

    if type == 'add_yes':
        if db_new.get_worker_role(id) is not None:
            bot.edit_message_text(
                f'Админ с ID: {id} - уже есть!',
                chat_id, mes_id
            )
        else:
            db_new.add_worker(id, role)
            bot.edit_message_text('Успешно!', chat_id, mes_id)

    if type == 'delete_yes':
        if db_new.get_worker_role(id) is not None:
            db_new.del_worker(id)
            bot.edit_message_text('Успешно!', chat_id, mes_id)
        else:
            bot.edit_message_text(
                'Админа с таким ID не существует!',
                chat_id, mes_id
            )

    if type == 'add_no' or type == 'delete_no':
        bot.edit_message_text('Отменено!', chat_id, mes_id)

    if '_yes' in type or '_no' in type:
        if role == 1:
            send_admin_workers_admin(bot, call.message, user_id, True)
        elif role == 2:
            send_admin_workers_redactors(bot, call.message, user_id, True)

    # Тех. поддержка
    if type == 'update_support':
        bot.set_state(user_id, AdminWorkersState.update_support, chat_id)
        bot.edit_message_text(
            'Отправьте id для тех. поддержки:',
            chat_id, mes_id,
            reply_markup=kb_admin_workers_back(3)
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminWorkersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_workers=admin_workers_factory.filter())
