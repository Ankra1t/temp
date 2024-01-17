import threading
import time
import os
from datetime import datetime
from AuthRoles import check_registrate
from MAIN.start import send_start_by_user


from initialize import bot, db, pays, pays_banker, pay_guard
from variables import *
from telebot import custom_filters, types
from telebot.types import Message

from config_logger import logger
from config_global import _ENV

import datetime as dt

from MAIN.states import AdminPostsState
from MAIN.commands import commands_registration
from MAIN.handlers import handlers_registration
from MAIN.callbacks import (
    callbacks_registration, kb_posts_back,
    send_admin_post, kb_cancel, choose_calculate_step,
)
from MAIN.common.utils import get_post_from_message
from common.utils import set_state_data

from keyboard_reply import *
from cb_filters import (AdminDefaultCallbackFilter, AdminWorkerssCallbackFilter,
                        AdminActionsCallbackFilter,
                        ClientActionsCallbackFilter, AdminMainCallbackFilter)

from messages.users import (paid_subscribe_msg, end_trial_subscribe_msg,
                            end_paid_subscribe_msg)
from messages.workers import (admin_fut_posts_msg, admin_users_msg,
                              redactor_main_msg, admin_posting_msg)

from BlockTGBotSender import BlockTGBotSender
from AuthMiddleWare import AuthMiddleWare

from models import Post, Update, User, UpdateBBanker


# TODO - переписать db
# TODO - отформатировать этот файл
# TODO - удаление тарифа
# TODO - продумать все отлавливания ошибок
# TODO - в callbacks -> keyboards удалить импорт kb_inl_admin


bot.setup_middleware(AuthMiddleWare(bot, db))

commands_registration(bot)
handlers_registration(bot)
callbacks_registration(bot)


# ======================= // ANCHOR Обработка команд
# Обработать успешный платеж через CryptoBot
@pays.pay_handler()
def invoice_paid_prev(update: Update) -> None:

    # print(f'update_info ')
    # print(update)
    # print(f'update.payload по сути оплаченный чек')
    # print(update.payload)

    # Найти по invoice_id транзакцию
    if update.payload.status == 'paid':

        transaction = pays.get_wait_transaction_for_complete(update)

        if transaction:
            logger.info('-----> Нашли нужную транзакцию '
                        'далее transactions_complete [{}]'.format(transaction['transaction_id']))

            # Завершаем транзакцию
            pays.transactions_complete(transaction['transaction_id'])

            # Добавить платную подписку
            finish_date_obj = pay_guard.set_paid_subscribe(transaction)
            finish_date = finish_date_obj.strftime('%d/%m/%Y')
            logger.info(f'-----> Добавили пользователю платную подписку')

            # Обнуляем пробную подписку
            trial_id = pay_guard.check_trial_active_by_user(
                transaction['user_id'])
            if trial_id:
                logger.info(
                    f'-----> Обнулили пробную подписку trial_id [{trial_id}]')
                pay_guard.set_subscribe_unactive(trial_id)

            # Отправляем сообщение пользователю
            bot.send_message(transaction['user_id'],
                             text=paid_subscribe_msg(finish_date),
                             parse_mode="HTML")

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
                        'далее transactions_complete [{}]'.format(transaction['transaction_id']))

            bot.send_message(transaction['user_id'],
                             text='Ваш платеж подтвержден и находиться в обработке',
                             parse_mode="HTML")

            # Завершаем транзакцию
            pays_banker.transactions_complete(transaction['transaction_id'])

            # Добавить платную подписку
            finish_date_obj = pay_guard.set_paid_subscribe(transaction)
            finish_date = finish_date_obj.strftime('%d/%m/%Y %d/%m/%Y в %H:%i')
            logger.info(f'-----> Добавили пользователю платную подписку')

            # Обнуляем пробную подписку
            trial_id = pay_guard.check_trial_active_by_user(
                transaction['user_id'])
            if trial_id:
                logger.info(
                    f'-----> Обнулили пробную подписку trial_id [{trial_id}]')
                pay_guard.set_subscribe_unactive(transaction['user_id'])

            # Отправляем сообщение пользователю
            bot.send_message(transaction['user_id'],
                             text=paid_subscribe_msg(finish_date),
                             parse_mode="HTML")

        else:
            logger.error(f'-----> Не нашли транзакцию по параметрам чека {update.payload} '
                         f'и статусу status "wait_payments"  ')

    # todo-fin: Сообщению пользователю: "Ваш счет в статусе не оплачен"


@bot.message_handler(content_types=['photo', 'video', 'text'])
def livepost_media(message: Message, data):
    user_role = data.get('user_role')

    if (user_role == 1 or user_role == 2) and message.text not in text_commands_stack:
        get_admin_livepost(message)


# ============================================ Доп.функции
# ================== Прием и отправка быстрого поста
def get_admin_livepost(message: types.Message):
    logger.info(f'Принимаем текст для быстрой отправки')

    chat_id = message.chat.id
    user_id = message.from_user.id

    post = get_post_from_message(bot, message)

    if post is None:
        bot.send_message(
            chat_id, 'Ошибка, попробуйте снова:',
            reply_markup=kb_live_cancel()
        )
        return

    state_data = {'post': post, 'kind': 'live'}
    bot.set_state(user_id, AdminPostsState.live, chat_id)
    set_state_data(bot, user_id, chat_id, state_data)

    bot.send_message(
        chat_id, 'Выберите действие:',
        reply_markup=kb_admin_livepost_request()
    )


# ======================== ПЛАНОВЫЕ ФУНКЦИИ ==============
def check_future_post_for_sent():
    lose_hours = 4
    date_now = dt.datetime.now()
    lose_time_back = date_now - dt.timedelta(hours=lose_hours)

    mas_posts = db.get_fut_all_posts()

    for post in mas_posts:
        date_post = post[4]
        date_post = date_post.split('.')
        time_post = post[5]
        time_post = time_post.split(':')
        delayed_time_obj = dt.datetime(int(date_post[2]), int(date_post[1]),
                                       int(date_post[0]), int(time_post[0]), int(time_post[1]))

        if (date_now > delayed_time_obj) and (delayed_time_obj > lose_time_back):
            send_future_pos_by_intime(post)
            db.del_fut_post(post[0])
            # Написать админу, что отложенный пост отправлен
            # bot.send_message(chat_id, f'Успешно!')
            print(
                f'-----> Отправляем пост [{post[0]}] c меткой времени [{post[4]}] и спим 10 сек')
            time.sleep(10)
        elif date_now < delayed_time_obj:
            pass
        elif (date_now > delayed_time_obj) and (delayed_time_obj < lose_time_back):
            pass
    return True


def send_future_pos_by_intime(post):
    """Рассылка отложенных постов по времени"""
    users_id = list(map(lambda user: user[9], pay_guard.get_paid_users()))

    try:
        tgsender = BlockTGBotSender(
            users_id, post[2], post[1], post[6], post[7], post[8])

        tgsender.send()
    except Exception as e:
        logger.error(
            f'Ошибка -send_future_pos_by_intime- в балансировщике при рассылке [{e}]')
    pass


def check_finish_trial_subscribe():
    users = list(map(lambda user: user[9],
                 pay_guard.get_users_note_fin_trial()))
    if users:
        logger.info(f'-----> Нашли пользователей для уведомлений ')

        new_admin_post = end_trial_subscribe_msg()

        try:
            tgsender = BlockTGBotSender(
                users, new_admin_post, '(text)', 'post')

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
        fin_date_obj = datetime.now()
        fin_date = fin_date_obj.strftime('%d.%m.%Y')

        new_admin_post = end_paid_subscribe_msg(fin_date)
        try:
            tgsender = BlockTGBotSender(
                users, new_admin_post, '(text)', 'post')

            tgsender.send()
        except Exception as e:
            logger.error(
                f'Ошибка -check_finish_paid_subscribe- в балансировщике при рассылке [{e}]')
        pass

        # После рассылки убрать активность ПЛАТНЫХ рассылок у данных пользователей
        pay_guard.set_paid_subscribe_unactive_many_users()


# Импортировать свой обработчик колбэков
import cb_client
import cb_admin

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.add_custom_filter(AdminMainCallbackFilter())
bot.add_custom_filter(AdminWorkerssCallbackFilter())

bot.add_custom_filter(AdminDefaultCallbackFilter())
bot.add_custom_filter(AdminActionsCallbackFilter())

bot.add_custom_filter(ClientActionsCallbackFilter())


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()  # (default "./.handlers-saves/step.save")


# =============================== //ANCHOR - Обработка INLINE
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    user_role = check_registrate(user_id) or 0

    global new_admin_post, new_admin_post_img, new_admin_type, new_admin_post_video
    global new_post, new_post_img, new_fut_post, new_fut_post_img, new_fut_post_time, new_fut_post_date
    global link, index_term

    if call.data == 'RUB' or call.data == 'USD':
        set_state_data(bot, user_id, chat_id, {'val_dep': call.data})
        bot.edit_message_text(
            'Введите размер депозита:', chat_id, mes_id,
            reply_markup=kb_cancel(user_id)
        )
        choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    if call.data == 'adm_posting':
        count_posts = len(db.get_fut_all_posts())
        bot.send_message(
            chat_id,
            text=admin_posting_msg(count_posts),
            reply_markup=kb_admin_posting()
        )

    if call.data == 'redactor_main':
        count_fut_posts = len(db.get_fut_all_posts())
        bot.send_message(
            chat_id,
            text=redactor_main_msg(count_fut_posts),
            reply_markup=kb_main_redactor()
        )

    # ========================================================================  ПОСТИНГ
    # ============================================= Рассылка live поста
    if call.data == 'live_send_now':
        bot.edit_message_text('Отправка...', chat_id, mes_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            kind = data.get('kind') or ''
            post: Post = data.get('post')

        tg_sender = BlockTGBotSender(
            [], post.content, f'{post.media or ""}({post.mes_type})', kind
        )
        tg_sender.send()

        bot.edit_message_text('Успешно отправлен!', chat_id, mes_id)
        bot.delete_state(user_id, chat_id)

    if call.data == 'live_signal':
        bot.edit_message_text(
            'Введите название сигнала:',
            chat_id, mes_id,
            reply_markup=kb_live_cancel()
        )
        bot.set_state(user_id, AdminPostsState.name, chat_id)

    if call.data == 'live_cancel':
        bot.delete_state(user_id, chat_id)
        bot.edit_message_text('Отменено!', chat_id, mes_id)
        send_start_by_user(bot, call.message, user_id, chat_id, user_role)

    if call.data == 'admin_posting_fut_post_all_show':
        # ## Показать список отложенных постов

        # Отобразить список постов
        mas_posts = db.get_fut_all_posts()
        logger.info(f'Массив постов посмотреть')
        logger.info(mas_posts)

        if len(mas_posts) != 0:
            for i in range(0, len(mas_posts)):
                mas_post_slice = mas_posts[i]

                # logger.info(f'Массив постов посмотреть mas_post_slice после подрезки')
                # logger.info(mas_post_slice)
                # logger.info(f'тип mas_post_slice {type(mas_post_slice)}')

                send_admin_post(bot, chat_id, *mas_post_slice)

        else:
            bot.send_message(chat_id,
                             text='Нет отложенных постов')

        bot.send_message(chat_id, admin_fut_posts_msg(),
                         reply_markup=kb_posts_back(), parse_mode='HTML')

    bot.answer_callback_query(call.id)


# Проверка рассылок каждые 15 сек - в отдельном потоке
def check_unfinit_tasks(param):
    sleep_time_check = 15
    while True:
        # check_finish_paid_subscribe()
        # check_finish_trial_subscribe()
        # check_future_post_for_sent()
        time.sleep(sleep_time_check)


thread_name = 'check_unfinit_tasks'
time.sleep(3)  # Чтобы поток успел запуститься
if 'check_unfinit_tasks' not in threading.enumerate():
    logger.info(
        f'-----> Запустили поток {thread_name} если он еще не запущен '
    )
    thread_id = threading.Thread(
        target=check_unfinit_tasks, name=thread_name, args=(thread_name,)
    ).start()

if _ENV == 'main':
    bot.infinity_polling()

try:
    if os.getenv("MODE_BOT") and os.getenv("MODE_BOT") == 'dev':
        bot.infinity_polling()
except Exception as e:
    print(f'Переменная окружения НЕ ЗАДАНА MODE_BOT == dev[{e}]')
    pass
    # logger.error(f'Ошибка  [{e}]')
