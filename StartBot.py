import threading
import time
from datetime import timedelta
from telebot import custom_filters, types

from NOTIFIER import notifier
from NOTIFIER.messages import mess_user_paid

from AuthRoles import check_registrate
from common.dt import get_datetime_now, get_str_by_datetime
from initialize import bot, pays, pays_banker, pay_guard

from db import db

from config_logger import logger

from MAIN.commands import commands_registration
from MAIN.handlers import handlers_registration
from MAIN.callbacks import callbacks_registration

from keyboard_reply import *

from messages.users import paid_subscribe_msg, end_trial_subscribe_msg, end_paid_subscribe_msg
from messages.workers import redactor_main_msg, admin_posting_msg

from Classes.BlockTGBotSender import BlockTGBotSender
from AuthMiddleWare import AuthMiddleWare

from models import Post, Update, UpdateBBanker


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

            tariff = db.get_price_by_id(
                transaction.price_id, None)  # type: ignore

            logger.info(f'-----> Добавили пользователю платную подписку')

            # Обнуляем пробную подписку

            pay_guard.set_trial_subscribe_unactive_by_user(
                transaction.user_id)
            # trial_id = pay_guard.check_trial_active_by_user(
            #     transaction['user_id'])
            # if trial_id:
            #     logger.info(
            #         f'-----> Обнулили пробную подписку trial_id [{trial_id}]')
            #     pay_guard.set_subscribe_unactive(trial_id)

            # Отправляем сообщение пользователю
            bot.send_message(
                transaction.user_id,
                text=paid_subscribe_msg(
                    finish_date, tariff.name),  # type: ignore
            )

            # Сообщение в бот уведомлений об оплате
            summ_full = f"{transaction.sum} {transaction.currency}"
            user = db.get_user_by_tg_id(transaction.user_id)
            notifier.send_notification('text', mess_user_paid(
                user_id=user.id,  # type: ignore
                user_nike='@' + user.username if user.username else user.tg_id,  # type: ignore
                summ_paid=summ_full,
                tariff_name=tariff.name,  # type: ignore
                finish_date=finish_date
            ))

        else:
            logger.error(f'-----> Не нашли транзакцию по параметрам чека {update.payload} '
                         f'и статусу status "wait_payments"  ')


# Обработать успешный платеж через CryptoBot
@pays_banker.pay_handler()
def invoice_paid(update: UpdateBBanker) -> None:
    if update.payload is None:
        return

    # return True;
    # Найти по invoice_id транзакцию
    if update.payload.status == 'paid':

        transaction = pays_banker.get_wait_transaction_for_complete(update)

        if transaction:
            logger.info('-----> Нашли нужную транзакцию '
                        'далее transactions_complete [{}]'.format(transaction.id))

            bot.send_message(
                transaction.user_id,
                'Ваш платеж подтвержден и находиться в обработке'
            )

            # Завершаем транзакцию
            pays_banker.transactions_complete(transaction.id)

            # Добавить платную подписку
            finish_date_obj = pay_guard.set_paid_subscribe(transaction)
            finish_date = get_str_by_datetime(finish_date_obj)

            tariff = db.get_price_by_id(
                transaction.price_id, None)  # type: ignore

            logger.info(f'-----> Добавили пользователю платную подписку')

            # Обнуляем пробную подписку
            pay_guard.set_trial_subscribe_unactive_by_user(
                transaction.user_id)
            # trial_id = pay_guard.check_trial_active_by_user(
            #     transaction['user_id'])
            # if trial_id:
            #     logger.info(
            #         f'-----> Обнулили пробную подписку trial_id [{trial_id}]')
            #     pay_guard.set_subscribe_unactive(trial_id)
            # pay_guard.set_subscribe_unactive(transaction['user_id'])

            # Отправляем сообщение пользователю
            bot.send_message(
                transaction.user_id,
                text=paid_subscribe_msg(
                    finish_date, tariff.name),  # type: ignore
            )

            # Сообщение в бот уведомлений об оплате
            summ_full = f"{transaction.sum} {transaction.currency}"
            user = db.get_user_by_tg_id(transaction.user_id)
            notifier.send_notification('text', mess_user_paid(
                user_id=user.id,  # type: ignore
                user_nike='@' + user.username if user.username else user.tg_id,  # type: ignore
                summ_paid=summ_full,
                tariff_name=tariff.name,  # type: ignore
                finish_date=finish_date
            ))

        else:
            logger.error(f'-----> Не нашли транзакцию по параметрам чека {update.payload} '
                         f'и статусу status "wait_payments"  ')

    # todo-fin: Сообщению пользователю: "Ваш счет в статусе не оплачен"



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


def check_finish_trial_subscribe():
    users = list(map(lambda user: user[9],
                 pay_guard.get_users_note_fin_trial()))
    if users:
        text = end_trial_subscribe_msg()

        post = Post(
            content=text,
            mes_type='text',
        )

        try:
            tgsender = BlockTGBotSender(users, post)
            tgsender.send()
        except Exception as e:
            logger.error(
                f'Ошибка -check_finish_trial_subscribe- в балансировщике при рассылке [{e}]')
        pass

        pay_guard.set_subscribe_unactive_many_users()


def check_finish_paid_subscribe():
    users = list(map(lambda user: user[9],
                 pay_guard.get_users_note_fin_paid()))
    if users:
        fin_date = get_str_by_datetime(get_datetime_now())

        text = end_paid_subscribe_msg(fin_date)

        post = Post(
            content=text,
            mes_type='text',
        )

        try:
            tgsender = BlockTGBotSender(users, post)
            tgsender.send()
        except Exception as e:
            logger.error(
                f'Ошибка -check_finish_paid_subscribe- в балансировщике при рассылке [{e}]')
        pass

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
        # check_finish_paid_subscribe()
        # check_finish_trial_subscribe()
        # check_future_post_for_sent()
        check_tariff()
        print('check')
        time.sleep(sleep_time_check)


thread_id = threading.Thread(
    target=check_unfinit_tasks, name='check_unfinit_tasks'
).start()
