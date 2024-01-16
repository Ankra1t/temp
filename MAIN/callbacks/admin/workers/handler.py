from telebot import TeleBot
from telebot.types import CallbackQuery

from initialize import kb_inl_admin
from db import db
from common.utils import is_digit, set_state_data
from MAIN.states import AdminWorkersState

from .filter import admin_workers_factory, AdminWorkersCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data: dict = admin_workers_factory.parse(call.data)
    type = data['type'] or ''
    id = int(data.get('id', 0)) if is_digit(data.get('id', '')) else 0
    name = data['name'] or ''
    role = int(data.get('role', 0)) if is_digit(data.get('role', '')) else -1

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    # Удаление/Добавление
    if type == 'add_yes':
        if db.check_worker(id):
            bot.edit_message_text(
                f'Админ с ID: {id} - уже есть!', chat_id, mes_id)
        else:
            print(f'Добавляю админа: {name} {id}')
            db.add_worker(id, name, role)
            bot.edit_message_text('Успешно!', chat_id, mes_id)

    if type == 'add_no' or type == 'delete_no':
        bot.edit_message_text('Отменено!', chat_id, mes_id)

    if type == 'delete_yes':
        if db.check_worker(id):
            print(f'Удаляю админа: {id}')
            db.del_worker(id)
            bot.edit_message_text('Успешно!', chat_id, mes_id)
        else:
            bot.edit_message_text(
                'Админа с таким ID не существует!', chat_id, mes_id)

    if 'delete' in type or 'add' in type:
        if role == 1:
            text = 'Отправьте ID гл.админа'
            worker = 'admin'
        else:
            text = 'Отправьте ID редактора'
            worker = 'redactor'

        if 'add' in type:
            state = AdminWorkersState.add_id
        else:
            state = AdminWorkersState.delete_id

        markup = kb_inl_admin.workers_actions_back(worker)

        if type == 'add' or type == 'delete':
            bot.edit_message_text(text, chat_id, mes_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)

        bot.set_state(user_id, state, chat_id)
        set_state_data(bot, user_id, chat_id, {'role': role})

    if type == 'redactor_list':
        res = ''
        mas = db.get_redactors()

        for i in range(0, len(mas)):
            if mas[i][3] == 2:
                res += '\n' + str(mas[i][0]) + ' | ' + \
                    mas[i][1] + '\nДолжность: Редактор\n'

        if res == '':
            res = 'Редакторов нет!'

        bot.edit_message_text(res, chat_id, mes_id,
                              reply_markup=kb_inl_admin.workers_actions_back('redactor'))

    if type == 'admin_list':
        res = ''
        mas = db.get_all_workes()
        for i in range(0, len(mas)):
            role = mas[i][3]
            user_tg_id = mas[i][4]
            username = mas[i][2]
            if role == 1:
                res += 'ID: ' + str(user_tg_id) + ' | Username: ' + \
                    username + ' | Должность: Гл.админ\n'

        bot.edit_message_text(res, chat_id, mes_id,
                              reply_markup=kb_inl_admin.workers_actions_back('admin'))

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminWorkersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_workers=admin_workers_factory.filter())
