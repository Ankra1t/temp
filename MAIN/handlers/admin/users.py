from telebot import TeleBot
from telebot.types import Message

from db import db
from initialize import kb_inl_admin, pay_guard
from models import User

from MAIN.states import AdminUsersState
from MAIN.callbacks import kb_admin_users_back, send_admin_client, kb_admin_users_cancel
from CALCULATE.common.messages import msg_digit_error
from common.utils import digit_accept, is_digit, set_state_data, text_accept
from messages.users import gift_subscribe_msg


def handle_client_search(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    with bot.retrieve_data(user_id, chat_id) as data:
        filter = data.get('filter') or ''
        page = data.get('page') or 1

    client_name_id = text_accept(message)
    if client_name_id is None:
        bot.send_message(
            chat_id,
            'Введите id или имя пользователя текстом:',
            reply_markup=kb_admin_users_cancel(filter, page)
        )
        return

    if is_digit(client_name_id):
        client_id = int(float(client_name_id))
        client = db.get_user_by_id(client_id)
    else:
        client_name_id = client_name_id.replace('@', '')
        client = db.get_user_by_username(client_name_id)

    if client is None:
        bot.send_message(
            chat_id,
            'Пользователя не существует.\nВведите id или имя пользователя:',
            reply_markup=kb_admin_users_cancel(filter, page)
        )
        return

    send_admin_client(
        bot, message, user_id,
        client[9], True,
        filter, page
    )

    bot.delete_state(user_id, chat_id)


def handle_days_subscribe(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    days = digit_accept(message, int)

    if days is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_admin_users_back()
        )
        return

    if days <= 0:
        bot.send_message(
            chat_id, 'Введите число больше нуля:',
            reply_markup=kb_admin_users_back()
        )

    with bot.retrieve_data(user_id, chat_id) as data:
        subscribe_user_id = data.get('user_id')

    pay_guard.set_subscribe_unactive_by_user_id(subscribe_user_id)

    datetime_show = pay_guard.set_custom_paid_subscribe(
        subscribe_user_id, int(days)
    )

    data_fin = datetime_show['admin']
    bot.send_message(
        chat_id,
        f'Клиенту с id[{subscribe_user_id}] установлена платная подписка на {days} дней, до {data_fin}'
    )
    send_admin_client(bot, message, user_id, subscribe_user_id, True)

    bot.send_message(
        subscribe_user_id,
        gift_subscribe_msg(datetime_show['user'])
    )

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_client_search, state=AdminUsersState.client_search)

    reg_mes(handle_days_subscribe, state=AdminUsersState.subscribe_days)
