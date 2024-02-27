from telebot import TeleBot
from telebot.types import Message

from db_new import db_new

from MAIN.common.utils import get_print_signal_info
from common.dt import get_str_by_datetime
from messages.workers import menu_msg
from models import Post

from .users.keyboards import kb_admin_client_info
from .workers.keyboards import kb_admin_workers, kb_admin_workers_actions, kb_admin_workers_support


def send_admin_post(
    bot: TeleBot, chat_id: int, post: Post
):
    text = '\n'.join((
        '\n'.join((
            f'<b>{post.details.name}</b>' if post.details is not None else '',
            f'👉 {post.details.ticker}' if post.details is not None else '',
            '',
            get_print_signal_info(post.details.open_price,
                                  post.details.stop_loss),
            '',
        )) if post.details is not None else '',
        post.content,
        '',
        f'ID: <b>{post.id}</b>\n' if post.id is not None else ''
        f'Тип: <b>{"Сигнал" if post.details is None else "Пост"}</b>',
        f'Дата и время поста: <b>{get_str_by_datetime(post.date_time)}</b>\n' if post.date_time is not None else ''
        f'Ограничение: <b>{post.direct}</b>',
    ))

    if post.mes_type == 'photo':
        bot.send_photo(
            chat_id, post.media,
            caption=text
        )
    elif post.mes_type == 'video':
        bot.send_video(
            chat_id, post.media,
            caption=text
        )
    else:
        bot.send_message(chat_id, text)


def send_admin_client(
    bot: TeleBot,
    message: Message,
    user_id: int,
    client_db_id: int,
    is_first=False,
    sort_by='',
    page=1
):
    chat_id = message.chat.id
    mes_id = message.id

    client = db_new.get_user_by_id(client_db_id)
    if client is None:
        return

    user_subsribe = db_new.get_current_subscribe_user(client.id)

    fin_date = 'нет'
    type_subscribe_show = ''

    if user_subsribe is not None:
        fin_date = get_str_by_datetime(user_subsribe.finish_dt)
        type_subscribe_show = f' тип {user_subsribe.type}'

    nikname = f'@{client.username}' if client.username != '' else ''
    count_ref = len(db_new.get_user_referals(client_db_id))
    is_banned = client.ban == 1

    text = '\n'.join((
        f'Пользователь <b>{nikname} | {client.id} {"(BAN)" if is_banned else ""}</b>',
        f'Подписка: {fin_date}{type_subscribe_show}',
        # f'Баланс: <b>{balance}</b>',
        f'Рефералов: <b>{count_ref}</b>',
        '',
        '<b>Выберите действие 👇</b>'
    ))
    keyboard = kb_admin_client_info(client_db_id, is_banned, page, sort_by)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


def send_admin_workers(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    text = menu_msg('Работники')
    keyboard = kb_admin_workers()

    if is_first:
        bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )

    bot.delete_state(user_id, chat_id)


def send_admin_workers_admin(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    res = '<b>Админы</b>\n'
    admins = db_new.get_admins()

    if len(admins) != 0:
        for i in range(0, len(admins)):
            res += f'\nID: {admins[i].id} | Username: @{admins[i].username}'
    else:
        res = '\nНет админов!'

    keyboard = kb_admin_workers_actions(1)

    if is_first:
        bot.send_message(chat_id, res, reply_markup=keyboard)
    else:
        bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=keyboard
        )

    bot.delete_state(user_id, chat_id)


def send_admin_workers_redactors(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    res = '<b>Редакторы</b>\n'
    redactors = db_new.get_redactors()

    if len(redactors) != 0:
        for i in range(0, len(redactors)):
            res += f'\nID: {redactors[i].id} | Username: @{redactors[i].username}'
    else:
        res = '\nНет редакторов!'

    keyboard = kb_admin_workers_actions(2)

    if is_first:
        bot.send_message(chat_id, res, reply_markup=keyboard)
    else:
        bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=keyboard
        )

    bot.delete_state(user_id, chat_id)


def send_admin_workers_support(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    sup = db_new.get_support_name()
    sup_link = f'@{sup}' if sup != '' else '-'

    text = f'Тех. поддержка: {sup_link}'
    keyboard = kb_admin_workers_support()

    if is_first:
        bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )

    bot.delete_state(user_id, chat_id)
