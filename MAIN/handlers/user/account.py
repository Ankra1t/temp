import re
from telebot import TeleBot
from telebot.types import Message

from CALCULATE.common.messages import msg_success_edit
from db import db
from MAIN.common.messages import msg_enter_nickname
from MAIN.states import UserAccountState
from MAIN.callbacks import send_user_account, kb_user_params_back, send_user_params
from common.utils import text_accept
from services import auth


def handle_new_password(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_pass = text_accept(message)

    if new_pass is None:
        bot.send_message(chat_id, 'Пароль должен быть строкой:')
        return

    if len(new_pass) < 8:
        bot.send_message(
            chat_id, 'Пароль должен состоять из 8 и более символов:'
        )
        return

    response = auth.change_password(user_id, new_pass)

    if response:
        bot.send_message(chat_id, 'Пароль успешно изменен')
    else:
        bot.send_message(chat_id, 'Ошибка!')

    send_user_account(bot, message, user_id, True)


def handle_nickname(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    nickname = text_accept(message)
    if nickname is None or not re.match(r'^[a-zA-Z0-9]+$', nickname):
        bot.send_message(
            chat_id, msg_enter_nickname(user_id, 'default'),
            reply_markup=kb_user_params_back(user_id)
        )
        return

    length_error = ''
    if len(nickname) < 4:
        length_error = 'min'
    elif len(nickname) > 16:
        length_error = 'max'

    if length_error != '':
        bot.send_message(
            chat_id, msg_enter_nickname(user_id, length_error),
            reply_markup=kb_user_params_back(user_id)
        )
        return

    user_db_id = db.get_user_id_by_tg_id(user_id)
    res = db.set_user_nickname(user_db_id, nickname)

    if res == 'Nickname has taken':
        bot.send_message(
            chat_id, msg_enter_nickname(user_id, 'taken'),
            reply_markup=kb_user_params_back(user_id)
        )
        return

    bot.send_message(chat_id, msg_success_edit(user_id))
    send_user_params(bot, message, user_id, True)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_password, state=UserAccountState.password)
    reg_mes(handle_nickname, state=UserAccountState.nickname)
