from telebot import TeleBot
from telebot.types import Message

from MAIN.states import UserAccountState
from MAIN.callbacks import send_user_account
from common.utils import text_accept

from AuthRoles import change_password


def handle_new_password(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_pass = text_accept(message)

    if new_pass is None:
        bot.send_message(chat_id, 'Пароль должен быть строкой:')
        return

    if len(new_pass) < 8:
        bot.send_message(
            chat_id, 'Пароль должен состоять из 8 и более символов:')
        return

    response = change_password(user_id, new_pass)

    if response:
        bot.send_message(chat_id, 'Пароль успешно изменен')
    else:
        bot.send_message(chat_id, 'Ошибка!')

    send_user_account(bot, message, user_id, True)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_password, state=UserAccountState.password)
