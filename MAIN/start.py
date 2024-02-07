from telebot import TeleBot
from telebot.types import Message

from initialize import pay_guard, base_statis, kb_inl_admin
from keyboard_reply import kb_main_redactor, kb_main_support
from db import db
from db_new import db_new

from MAIN.callbacks import send_user_main

from messages.users import welcome_trial_subscribe_msg
from messages.workers import admin_main_msg, redactor_main_msg, support_main_msg


def send_start_by_user(
        bot: TeleBot,
        message: Message,
        user_id: int,
        chat_id: int,
        user_role: int,
        has_registered_now=False
):
    bot.delete_state(user_id, chat_id)

    if user_role == 0:
        if has_registered_now:
            # bot.send_message(
            #     chat_id, welcome_trial_subscribe_msg()
            # )
            # todo-fin: Назначаем тестовую подписку
            pass

        send_user_main(bot, message, user_id, True)

    if user_role == 1:
        count_all = db_new.get_users_count()
        # todo-fin: Заменить кол-во транзакций на агрегацию пользователей (если у пользователя больше 2х подписок)
        count_with_sub = base_statis.count_payments()
        # count_with_sub = len(pay_guard.get_paid_users())
        count_old = len(pay_guard.get_paid_more1_users())
        count_old = 0
        count_admins = len(db_new.get_all_workes())
        count_fut_posts = len(db.get_fut_all_posts())
        count_fut_posts = 0

        text = admin_main_msg(count_all, count_with_sub,
                              count_old, count_admins, count_fut_posts)
        bot.send_message(chat_id, text, reply_markup=kb_inl_admin.main())

    if user_role == 2:
        count_fut_posts = len(db.get_fut_all_posts())
        bot.send_message(
            chat_id, redactor_main_msg(count_fut_posts),
            reply_markup=kb_main_redactor())

    if user_role == 3:
        count_order = 0
        # try:
        #     count_order = len(db.get_orders_sup())
        # except Exception as e:
        #     count_order = ''
        #     logger.error(f'Ошибка db.get_orders_sup() [{e}]')

        bot.send_message(
            chat_id, support_main_msg(count_order),
            reply_markup=kb_main_support()
        )
