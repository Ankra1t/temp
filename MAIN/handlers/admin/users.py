from telebot import TeleBot
from telebot.types import Message

from common.dt import get_str_by_datetime
from db import db
from Classes import pay_guard

from config_logger import logger

from MAIN.states import AdminUsersState
from MAIN.callbacks import kb_admin_users_back, send_admin_client, kb_admin_users_cancel
from CALCULATE.common.messages import msg_digit_error
from common.utils import digit_accept, is_digit, text_accept
from messages.users import gift_subscribe_msg, gift_trial_subscribe_msg


def handle_client_search(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        sort_by = data.get('sort_by') or ''
        page = data.get('page') or 1

    client_name_id = text_accept(message)
    if client_name_id is None:
        bot.send_message(
            chat_id,
            'Введите id или имя пользователя текстом:',
            reply_markup=kb_admin_users_cancel(sort_by, page)
        )
        return

    if is_digit(client_name_id):
        client_db_id = int(float(client_name_id))
    else:
        client_name_id = client_name_id.replace('@', '')
        client_db_id = db.get_user_id_by_tg_name(client_name_id)

    client = db.get_user_by_id(client_db_id)

    if client is None:
        bot.send_message(
            chat_id,
            'Пользователя не существует.\nВведите id или имя пользователя:',
            reply_markup=kb_admin_users_cancel(sort_by, page)
        )
        return

    send_admin_client(
        bot, message, user_id,
        client.id, True,
        sort_by, page
    )

    bot.delete_state(user_id, chat_id)


def handle_days_subscribe(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    days = digit_accept(message, int)
    current_state = bot.get_state(user_id, chat_id)

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
        tariff_id = data.get('tariff_id')
        subscribe_user_id = data.get('user_id')

    # Получить tg_user_id
    user = db.get_user_by_id(subscribe_user_id)
    if user is None:
        logger.error('[handle_days_subscribe]: не найден пользователь')
        return

    if current_state == 'AdminUsersState:subscribe_days':
        tariff = db.get_price_by_id(tariff_id)
        if tariff is None:
            return

        pay_guard.set_subscribe_unactive_by_user_id(user.tg_id)
        datetime_show = pay_guard.set_trial(
            user.tg_id, tariff.type_product, int(days)
        )

        data_fin = get_str_by_datetime(datetime_show)
        bot.send_message(
            chat_id,
            f'Клиенту с id[{subscribe_user_id}] установлена платная подписка на {days} дней, до {data_fin}'
        )
        send_admin_client(bot, message, user_id, subscribe_user_id, True)

        bot.send_message(
            user.tg_id,
            gift_subscribe_msg(user.tg_id, data_fin)
        )

    if current_state == 'AdminUsersState:trial_subscribe_days_get_days':
        try:
            pay_guard.deactivate_user_trial_subscribe(user.id)
            finish_dt = pay_guard.set_trial(user.id, 'calc', days)  # TODO

            data_fin = get_str_by_datetime(finish_dt)
            bot.send_message(
                chat_id,
                f'Клиенту с id[{subscribe_user_id}] установлена пробная подписка на {days} дней, до {data_fin}'
            )
            send_admin_client(bot, message, user_id, subscribe_user_id, True)

            bot.send_message(
                user.tg_id, gift_trial_subscribe_msg(user.tg_id, data_fin)
            )
        except Exception as e:
            logger.error(f'Что то пошло не так {e}')
            pass

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_client_search, state=AdminUsersState.client_search)

    reg_mes(handle_days_subscribe, state=AdminUsersState.subscribe_days)

    reg_mes(handle_days_subscribe,
            state=AdminUsersState.trial_subscribe_days_get_days)
