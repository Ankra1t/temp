from telebot import TeleBot
from telebot.types import Message

from db_new import db_new

from MAIN.states import AdminWorkersState
from MAIN.callbacks import kb_admin_workers_confirm, kb_admin_workers_back, send_admin_workers_support
from common.utils import digit_accept, set_state_data, text_accept


def handle_add_id(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    id = digit_accept(message, int)

    with bot.retrieve_data(user_id, chat_id) as data:
        current_role = data.get('role', 2)

    if id is None:
        bot.send_message(
            chat_id, 'Введите чисо:',
            reply_markup=kb_admin_workers_back(current_role)
        )
        return

    set_state_data(bot, user_id, chat_id, {'id': id})
    bot.set_state(user_id, AdminWorkersState.add_name, chat_id)
    bot.send_message(
        chat_id, 'Введите никнейм:',
        reply_markup=kb_admin_workers_back(current_role)
    )


def handle_add_name(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    name = text_accept(message)

    with bot.retrieve_data(user_id, chat_id) as data:
        id = data.get('id')
        current_role = data.get('role', 2)

    if name is None:
        bot.send_message(
            chat_id, 'Отправьте текст:',
            reply_markup=kb_admin_workers_back(current_role)
        )
        return

    bot.delete_state(user_id, chat_id)
    bot.send_message(
        chat_id, f'Добавить <b>@{name}</b> с id: <b>{id}</b>?',
        reply_markup=kb_admin_workers_confirm(id, name, current_role, 'add')
    )


def handle_delete_id(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    id = digit_accept(message, int)

    with bot.retrieve_data(user_id, chat_id) as data:
        current_role = data.get('role', 2)

    if id is None:
        bot.send_message(
            chat_id, 'Введите чисо:',
            reply_markup=kb_admin_workers_back(current_role))
        return

    bot.delete_state(user_id, chat_id)
    bot.send_message(
        message.chat.id, text=f'Удалить <b>{id}</b>?',
        reply_markup=kb_admin_workers_confirm(
            id, '', current_role, action='delete')
    )


def handle_support_name(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    support_name = text_accept(message)
    if support_name is None:
        bot.send_message(
            chat_id, 'Введите ник текстом:'
        )
        return

    support_name = support_name.replace('@', '')
    db_new.update_support_name(support_name)

    bot.delete_state(user_id, chat_id)
    send_admin_workers_support(bot, message, user_id, True)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_add_id, state=AdminWorkersState.add_id)
    reg_mes(handle_add_name, state=AdminWorkersState.add_name)

    reg_mes(handle_delete_id, state=AdminWorkersState.delete_id)

    reg_mes(handle_support_name, state=AdminWorkersState.update_support)
