from telebot import TeleBot
from telebot.types import Message
from MAIN.callbacks.admin.users.keyboards import kb_admin_users_cancel

from db import db
from initialize import kb_inl_admin, pay_guard
from models import User

from MAIN.states import AdminUsersState
from MAIN.callbacks import kb_admin_users_back, send_admin_client
from CALCULATE.common.messages import msg_digit_error
from common.utils import digit_accept, is_digit, set_state_data, text_accept
from messages.users import gift_subscribe_msg


def handle_client_search(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    with bot.retrieve_data(user_id, chat_id) as data:
        filter = data.get('filter') or ''
        page = data.get('page') or 1

    client_name_id = text_accept(message)
    if client_name_id is None:
        bot.send_message(
            chat_id,
            'Введите id или имя пользователя текстом:',
            reply_markup=kb_admin_users_cancel(filter, page)
        )
        return

    if is_digit(client_name_id):
        client_id = int(float(client_name_id))
        client = db.get_user_by_id(client_id)
    else:
        client_name_id = client_name_id.replace('@', '')
        client = db.get_user_by_username(client_name_id)

    if client is None:
        bot.send_message(
            chat_id,
            'Пользователя не существует.\nВведите id или имя пользователя:',
            reply_markup=kb_admin_users_cancel(filter, page)
        )
        return

    send_admin_client(
        bot, message, user_id,
        client[9], True,
        filter, page
    )

    bot.delete_state(user_id, chat_id)


def handle_username_subscribe(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    username = text_accept(message)

    if username is None:
        bot.send_message(
            chat_id, 'Введите ник текстом:',
            reply_markup=kb_admin_users_back()
        )
        return

    username = username.replace('@', '')

    subscribe_user_id = pay_guard.get_user_id_by_username(username)

    if subscribe_user_id:
        set_state_data(bot, user_id, chat_id, {
            'user_id': subscribe_user_id,
            'username': username
        })
        bot.send_message(
            chat_id,
            'Количество дней подписки:',
            reply_markup=kb_admin_users_back()
        )
        bot.set_state(user_id, AdminUsersState.subscribe_days, chat_id)
    else:
        bot.send_message(
            chat_id,
            'Такого пользователя не существует, попробуйте другой username',
            reply_markup=kb_admin_users_back()
        )


def handle_days_subscribe(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    days = digit_accept(message, int)

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
        subscribe_user_id = data.get('user_id')

    pay_guard.set_subscribe_unactive_by_user_id(subscribe_user_id)

    datetime_show = pay_guard.set_custom_paid_subscribe(
        subscribe_user_id, int(days)
    )

    data_fin = datetime_show['admin']
    bot.send_message(
        chat_id,
        f'Клиенту с id[{subscribe_user_id}] установлена платная подписка на {days} дней, до {data_fin}'
    )
    send_admin_client(bot, message, user_id, subscribe_user_id, True)

    bot.send_message(
        subscribe_user_id,
        gift_subscribe_msg(datetime_show['user'])
    )

    bot.delete_state(user_id, chat_id)


def handle_user_id_subscribe_update(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_sub_id = digit_accept(message, int)

    if user_sub_id is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_admin_users_back()
        )
        return

    if not db.check_user(user_sub_id):
        bot.send_message(
            chat_id,
            'Пользователя с таким ID не существует!\nОтправьте корректный ID',
            reply_markup=kb_admin_users_back()
        )
        return

    user = User()
    user.id = user_sub_id
    user = pay_guard.get_current_subscribe_user(user)

    if user is None or user.subscribe is None:
        bot.send_message(
            chat_id, 'Пользователь с таким ID не имеет активных подписок',
            reply_markup=kb_admin_users_back()
        )
        return

    finish_date_obj = user.subscribe.finish_dt
    fin_date = finish_date_obj.strftime('%d/%m/%Y')

    bot.send_message(
        chat_id, f'У этого пользователя подписка заканчивается: {fin_date}'
    )
    bot.send_message(
        chat_id,
        'Отправьте количество дней, которые надо добавить/убавить в подписке',
        reply_markup=kb_admin_users_back()
    )
    set_state_data(bot, user_id, chat_id, {'user': user})
    bot.set_state(user_id, AdminUsersState.sub_days, chat_id)


def handle_days_subscribe_update(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    days = digit_accept(message, int)

    if days is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_admin_users_back()
        )
        return

    if days <= 0:
        bot.send_message(
            chat_id,
            'Неправильно введены дни или 0 дней слишком мало',
            reply_markup=kb_admin_users_back()
        )

    with bot.retrieve_data(user_id, chat_id) as data:
        user: User = data.get('user')
        user.subscribe_days = days
        data['user'] = user

    bot.send_message(
        chat_id,
        f'{days} дней подписки',
        reply_markup=kb_inl_admin.kb_add_sub_subscribe()
    )
    bot.set_state(user_id, AdminUsersState.sub_choice, chat_id)


def handle_ban_username(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    username = text_accept(message)

    if username is None:
        bot.send_message(
            chat_id, 'Введите ник текстом:',
            reply_markup=kb_admin_users_back()
        )
        return

    username = username.replace('@', '')

    user_ban_id: int | None = pay_guard.get_user_id_by_username(username)

    if user_ban_id is None:
        bot.send_message(
            chat_id,
            'Такого пользователя не существует, попробуйте другой username',
            reply_markup=kb_admin_users_back()
        )
        return

    pay_guard.ban_user_by_id(user_ban_id)

    bot.send_message(
        chat_id,
        f'Пользователь {username} id {user_id} забанен',
        reply_markup=kb_inl_admin.kb_success_ban_actions()
    )
    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_client_search, state=AdminUsersState.client_search)

    reg_mes(handle_username_subscribe,
            state=AdminUsersState.subscribe_username)
    reg_mes(handle_days_subscribe, state=AdminUsersState.subscribe_days)

    reg_mes(handle_user_id_subscribe_update, state=AdminUsersState.sub_user_id)
    reg_mes(handle_days_subscribe_update, state=AdminUsersState.sub_days)

    reg_mes(handle_ban_username, state=AdminUsersState.ban_username)
