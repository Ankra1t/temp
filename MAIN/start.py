from telebot import TeleBot
from telebot.types import Message

from keyboard_reply import kb_main_redactor, kb_main_support
from db_new import db_new

from MAIN.callbacks import send_user_main, send_admin_main

from messages.workers import redactor_main_msg, support_main_msg


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

    if user_role == 1:
        send_admin_main(bot, message, user_id, True)

    if user_role == 2:
        count_fut_posts = len(db_new.get_all_posts())
        bot.send_message(
            chat_id, redactor_main_msg(count_fut_posts),
            reply_markup=kb_main_redactor())

    if user_role == 3:
        count_order = 0
        # try:
        #     count_order = len(db_old.get_orders_sup())
        # except Exception as e:
        #     count_order = ''
        #     logger.error(f'Ошибка db_old.get_orders_sup() [{e}]')

        bot.send_message(
            chat_id, support_main_msg(count_order),
            reply_markup=kb_main_support()
        )
