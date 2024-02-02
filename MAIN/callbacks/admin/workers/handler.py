from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new

from common.utils import is_digit, set_state_data
from MAIN.states import AdminWorkersState

from .filter import admin_workers_factory, AdminWorkersCallbackFilter
from .keyboards import kb_admin_workers_actions, kb_admin_workers_back
from ..pages import send_admin_workers, send_admin_workers_support


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = admin_workers_factory.parse(call.data)

    type = data.get('type', '')
    id = int(data.get('id', 0)) if is_digit(data.get('id', '')) else 0
    name = data.get('name', '')
    role = int(data.get('role', -1)) if is_digit(data.get('role', '')) else -1

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'workers':
        send_admin_workers(bot, call.message)

    if type == 'admins':
        res = '<b>Админы</b>\n'
        admins = db_new.get_admins()

        if len(admins) != 0:
            for i in range(0, len(admins)):
                res += f'\nID: {admins[i].tg_id} | Username: @{admins[i].username}'
        else:
            res = '\nНет админов!'

        bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=kb_admin_workers_actions(1)
        )

    if type == 'redactors':
        res = '<b>Редакторы</b>\n'
        redactors = db_new.get_redactors()

        if len(redactors) != 0:
            for i in range(0, len(redactors)):
                res += f'\nID: {redactors[i].tg_id} | Username: @{redactors[i].username}\n'
        else:
            res = '\nНет редакторов!\n'

        bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=kb_admin_workers_actions(2)
        )

    if type == 'support':
        send_admin_workers_support(bot, call.message)

    if type == 'workers_list':
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

            res += f'\n@{mas[i].username} | {show_role}'

        bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=kb_admin_workers_back()
        )

    # Удаление/Добавление
    if type == 'delete' or type == 'add':
        if role == 1:
            text = 'Отправьте ID гл. админа'
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
            db_new.add_worker(id, name, role)
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

    # Тех. поддержка
    if type == 'update_support':
        bot.set_state(user_id, AdminWorkersState.update_support, chat_id)
        bot.edit_message_text(
            'Отправьте ник ТГ для тех. поддержки:',
            chat_id, mes_id,
            reply_markup=kb_admin_workers_back(3)
        )

    bot.clear_step_handler(call.message)
    bot.delete_state(user_id, chat_id)
    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminWorkersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_workers=admin_workers_factory.filter())
