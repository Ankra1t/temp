from telebot import TeleBot
from telebot.types import Message

from db_new import db_new
from initialize import pay_guard
from models import User

from MAIN.states import AdminUsersState
from MAIN.callbacks import kb_admin_users_back, send_admin_client, kb_admin_users_cancel
from CALCULATE.common.messages import msg_digit_error
from common.utils import digit_accept, is_digit, set_state_data, text_accept
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
        client_db_id = db_new.get_user_id_by_tg_name(client_name_id)

    client = db_new.get_user_by_id(client_db_id)

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
    user = db_new.get_user_by_id(subscribe_user_id)

    if current_state == 'AdminUsersState:subscribe_days':
        # !!! деактивировать старые платные и пробные подписки
        pay_guard.set_subscribe_unactive_by_user_id(user.tg_id, tariff_id)
        datetime_show = pay_guard.set_custom_paid_subscribe(
            user.tg_id, tariff_id, int(days)
        )

        data_fin = datetime_show['admin']
        bot.send_message(
            chat_id,
            f'Клиенту с id[{subscribe_user_id}] установлена платная подписка на {days} дней, до {data_fin}'
        )
        send_admin_client(bot, message, user_id, subscribe_user_id, True)

        bot.send_message(
            user.tg_id,
            gift_subscribe_msg(datetime_show['user'])
        )

    if current_state == 'AdminUsersState:trial_subscribe_days_get_days':
        try:
            pay_guard.set_trial_subscribe_unactive_by_user(user.tg_id)
            datetime_show = pay_guard.set_trial(user.tg_id, days)
            
            data_fin = datetime_show['admin']
            bot.send_message(
                chat_id,
                f'Клиенту с id[{subscribe_user_id}] установлена пробная подписка на {days} дней, до {data_fin}'
            )
            send_admin_client(bot, message, user_id, subscribe_user_id, True)

            bot.send_message(
                user.tg_id,
                gift_trial_subscribe_msg(datetime_show['user'])
            )
        except Exception as e:
            print(f'Что то пошло не так {e}')
            pass

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_client_search, state=AdminUsersState.client_search)

    reg_mes(handle_days_subscribe, state=AdminUsersState.subscribe_days)

    reg_mes(handle_days_subscribe, state=AdminUsersState.trial_subscribe_days_get_days)

