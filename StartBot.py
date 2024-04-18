import threading
import time
from datetime import timedelta
from telebot import custom_filters, types

from NOTIFIER import notifier
from NOTIFIER.messages import mess_user_paid

from AuthRoles import check_registrate
from common.dt import get_datetime_now, get_str_by_datetime
from initialize import bot, pays, pay_guard

from db import db

from config_logger import logger

from MAIN.commands import commands_registration
from MAIN.handlers import handlers_registration
from MAIN.callbacks import callbacks_registration

from keyboard_reply import *

from messages.users import paid_subscribe_msg, end_trial_subscribe_msg, end_paid_subscribe_msg
from messages.workers import redactor_main_msg, admin_posting_msg

from Classes.BlockTGBotSender import BlockTGBotSender, send_message_by_type
from AuthMiddleWare import AuthMiddleWare

from models import Post, Update


# TODO - отформатировать этот файл
# TODO - удаление тарифа
# TODO - продумать все отлавливания ошибок


bot.setup_middleware(AuthMiddleWare(bot))

commands_registration(bot)
callbacks_registration(bot)
handlers_registration(bot)

bot.add_custom_filter(custom_filters.StateFilter(bot))

# ======================= // ANCHOR Обработка команд
# Обработать успешный платеж через CryptoBot


@pays.pay_handler()
def invoice_paid_prev(update: Update) -> None:
    # Найти по invoice_id транзакцию
    if update.payload.status == 'paid':

        transaction = pays.get_wait_transaction_for_complete(update)

        if transaction:
            logger.info('-----> Нашли нужную транзакцию '
                        'далее transactions_complete [{}]'.format(transaction.id))

            bot.send_message(
                transaction.user_id,
                'Ваш платеж подтвержден и находиться в обработке'
            )

            # Завершаем транзакцию
            pays.transactions_complete(transaction.id)

            # Добавить платную подписку
            finish_date_obj = pay_guard.set_paid_subscribe(transaction)
            finish_date = get_str_by_datetime(finish_date_obj)

            logger.info(f'-----> Добавили пользователю платную подписку')

            # Обнуляем пробную подписку
            pay_guard.deactivate_user_trial_subscribe(
                transaction.user_id
            )

            # Отправляем сообщение пользователю
            bot.send_message(
                transaction.user_id,
                text=paid_subscribe_msg(
                    finish_date, transaction.name
                ),
            )

            # Сообщение в бот уведомлений об оплате
            summ_full = f"{transaction.sum} {transaction.currency}"
            user = db.get_user_by_tg_id(transaction.user_id)
            if user is not None:
                notifier.send_notification('text', mess_user_paid(
                    user_id=transaction.user_id,
                    user_nike='@' + user.username if user.username else user.tg_id,
                    summ_paid=summ_full,
                    tariff_name=transaction.name,
                    finish_date=finish_date
                ))

        else:
            logger.error(f'-----> Не нашли транзакцию по параметрам чека {update.payload} '
                         f'и статусу status "wait_payments"  ')


# ======================== ПЛАНОВЫЕ ФУНКЦИИ ==============
def check_future_post_for_sent():
    lose_hours = 4
    date_now = get_datetime_now()
    lose_time_back = date_now - timedelta(hours=lose_hours)

    mas_posts = db.get_all_posts()

    for post in mas_posts:
        if (post.date_time is not None) and (post.date_time < date_now) and (post.date_time > lose_time_back):
            send_future_pos_by_intime(post)
            db.delete_post(post.id or 0)

            # TODO - Написать админу, что отложенный пост отправлен
            time.sleep(10)

    return True


def send_future_pos_by_intime(post: Post):
    """Рассылка отложенных постов по времени"""
    users_id = list(map(lambda user: user.tg_id, pay_guard.get_paid_users()))

    try:
        tgsender = BlockTGBotSender(users_id, post)
        tgsender.send()
    except Exception as e:
        logger.error(
            f'Ошибка -send_future_pos_by_intime- в балансировщике при рассылке [{e}]')
    pass


# TODO - через класс рассылок
def check_finish_trial_subscribe():
    users = pay_guard.get_users_note_fin_trial()
    if len(users) == 0:
        return

    for user in users:
        try:
            send_message_by_type(
                bot, user.tg_id, 'text', end_trial_subscribe_msg(user.tg_id)
            )
        except:
            print('error sending message')

    pay_guard.set_subscribe_unactive_many_users()


# TODO - через класс рассылок
def check_finish_paid_subscribe():
    users = pay_guard.get_users_note_fin_paid()
    if len(users) == 0:
        return

    for user in users:
        try:
            send_message_by_type(
                bot, user.tg_id, 'text', end_paid_subscribe_msg(user.tg_id)
            )
        except:
            print('error sending message')

    # После рассылки убрать активность ПЛАТНЫХ рассылок у данных пользователей
    pay_guard.set_paid_subscribe_unactive_many_users()


def check_tariff():
    db.check_tariffs_datetime()


# =============================== //ANCHOR - Обработка INLINE
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    user_role = check_registrate(user_id) or 0

    if call.data == 'adm_posting':
        count_posts = len(db.get_all_posts())
        bot.send_message(
            chat_id,
            text=admin_posting_msg(count_posts),
            # reply_markup=kb_admin_posting()
            # Button("Платн: Новые посты")
            # Button("Отложенные посты")
            # Button("Всем: Сделать рассылку")
            # Button("Главная")
        )

    if call.data == 'redactor_main':
        count_fut_posts = len(db.get_all_posts())
        bot.send_message(
            chat_id,
            text=redactor_main_msg(count_fut_posts),
            reply_markup=kb_main_redactor()
        )

    bot.answer_callback_query(call.id)


# Проверка рассылок каждые 30 сек - в отдельном потоке
def check_unfinit_tasks():
    sleep_time_check = 30
    while True:
        check_finish_paid_subscribe()
        check_finish_trial_subscribe()
        check_tariff()
        time.sleep(sleep_time_check)


thread_id = threading.Thread(
    target=check_unfinit_tasks, name='check_unfinit_tasks'
).start()
