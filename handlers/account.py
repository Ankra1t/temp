import re
from telebot.async_telebot import AsyncTeleBot
from models import Message, StateContext, User

from db import db
from states.account import UserAccountState
from common.utils import text_accept
from services import auth

from keyboards.account import kb_user_params_back
from pages.user import send_user_account, send_user_params

from messages.common import msg_success_edit
from messages.profile import msg_enter_nickname


async def handle_new_password(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_pass = text_accept(message)

    if new_pass is None:
        await bot.send_message(chat_id, 'Пароль должен быть строкой:')
        return

    if len(new_pass) < 8:
        await bot.send_message(
            chat_id, 'Пароль должен состоять из 8 и более символов:'
        )
        return

    response = auth.change_password(userId=user_id, password=new_pass)

    if response:
        await bot.send_message(chat_id, 'Пароль успешно изменен')
    else:
        await bot.send_message(chat_id, 'Ошибка!')

    await send_user_account(bot, message, state, user, True)


async def handle_nickname(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    nickname = text_accept(message)
    if nickname is None or not re.match(r'^[a-zA-Z0-9]+$', nickname):
        await bot.send_message(
            chat_id, msg_enter_nickname(user.lang, 'default'),
            reply_markup=kb_user_params_back(user.lang)
        )
        return

    length_error = ''
    if len(nickname) < 4:
        length_error = 'min'
    elif len(nickname) > 16:
        length_error = 'max'

    if length_error != '':
        await bot.send_message(
            chat_id, msg_enter_nickname(user.lang, length_error),
            reply_markup=kb_user_params_back(user.lang)
        )
        return

    await bot.send_message(chat_id, msg_success_edit(user.lang))
    await send_user_params(bot, message, state, user, True)


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_password, state=UserAccountState.password)
    reg_mes(handle_nickname, state=UserAccountState.nickname)
