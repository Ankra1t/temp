from telebot import TeleBot
from telebot.types import Message

from MAIN.states import AdminWorkersState
from MAIN.callbacks import kb_admin_workers_update
from common.utils import digit_accept, set_state_data, text_accept

from initialize import kb_inl_admin


def _get_role(bot: TeleBot, user_id: int, chat_id: int):
    with bot.retrieve_data(user_id, chat_id) as data:
        role = data.get('role')
        if role is not None:
            role = int(role)
        else:
            role = -1

    worker = ''
    if role == 1:
        worker = 'admin'
    elif role == 2:
        worker = 'redactor'
    elif role == 3:
        worker = 'support'

    return worker


def handle_add_id(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    id = digit_accept(message, int)

    role = _get_role(bot, user_id, chat_id)
    if role is None:
        return

    if id is None:
        bot.send_message(
            chat_id, 'Введите чисо:',
            reply_markup=kb_inl_admin.workers_actions_back(role))
        return

    set_state_data(bot, user_id, chat_id, {'id': id})
    bot.set_state(user_id, AdminWorkersState.add_name, chat_id)
    bot.send_message(
        chat_id, 'Никнейм с @?',
        reply_markup=kb_inl_admin.workers_actions_back(role)
    )


def handle_add_name(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    name = text_accept(message)
    worker = _get_role(bot, user_id, chat_id)
    if name is None:
        bot.send_message(
            chat_id, 'Отправьте текст:',
            reply_markup=kb_inl_admin.workers_actions_back(worker))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        id = data.get('id')
        role = data.get('role')

    bot.delete_state(user_id, chat_id)
    bot.send_message(
        chat_id, f'Добавить {name} с id: {id}?',
        reply_markup=kb_admin_workers_update(id, name, role, 'add'))


def handle_delete_id(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    id = digit_accept(message, int)
    worker = _get_role(bot, user_id, chat_id)

    if id is None:
        bot.send_message(
            chat_id, 'Введите чисо:',
            reply_markup=kb_inl_admin.workers_actions_back(worker))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        role = data.get('role')

    bot.delete_state(user_id, chat_id)
    bot.send_message(
        message.chat.id, text=f'Удалить {id}?',
        reply_markup=kb_admin_workers_update(id, '', role, action='delete'))


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_add_id, state=AdminWorkersState.add_id)
    reg_mes(handle_add_name, state=AdminWorkersState.add_name)
    reg_mes(handle_delete_id, state=AdminWorkersState.delete_id)
