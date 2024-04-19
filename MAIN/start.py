from telebot import TeleBot
from telebot.types import Message

from MAIN.common.utils import send_in_development

from MAIN.callbacks import send_user_main, send_admin_main, send_site_code


def send_start_by_user(
        bot: TeleBot,
        message: Message,
        user_id: int,
        user_role: int,
        has_registered_now=False
):
    chat_id = message.chat.id
    bot.delete_state(user_id, chat_id)

    if user_role == 0:
        send_user_main(bot, message, user_id, True, has_registered_now)

    elif message.text is not None and len(message.text.split()) == 2:
        _, code = message.text.split()
        if code == 'site':
            send_site_code(bot, message, user_id, True)
            return

    elif user_role == 1:
        send_admin_main(bot, message, user_id, True)

    elif user_role == 2:
        send_in_development(bot, message)

    elif user_role == 3:
        send_in_development(bot, message)
