from typing import Literal
from telebot import TeleBot
from telebot.types import Message, InputMediaPhoto

from MAIN.common.messages import msg_admin_tariff
from common.utils import delete_message
from db import db
from initialize import pay_guard, base_statis

from MAIN.common.utils import get_print_signal_info
from common.dt import get_str_by_datetime
from messages.statistics import admin_main_statistics
from messages.workers import admin_fut_posts_msg, admin_main_msg, admin_users_msg, menu_msg
from models import Post

from .main.keyboards import kb_admin_main
from .tariffs.keyboards import kb_admin_tariffs, kb_admin_tariffs_back, kb_admin_tariffs_delete, kb_admin_tariffs_list, kb_admin_tariffs_edit
from .users.keyboards import kb_admin_client_info, kb_admin_users
from .workers.keyboards import kb_admin_workers, kb_admin_workers_actions, kb_admin_workers_support
from .statistics.keyboards import kb_statistics
from .posts.keyboards import kb_posts
from .params.keyboards import kb_params


def send_admin_main(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    count_all = db.get_users_count()
    count_admins = len(db.get_all_workes())
    count_fut_posts = len(db.get_all_posts())

    count_old = len(pay_guard.get_paid_more1_users())
    count_with_sub = base_statis.count_payments_dry()

    keyboard = kb_admin_main()
    text = admin_main_msg(
        count_all, count_with_sub, count_old,
        count_admins, count_fut_posts
    )

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


def send_admin_users(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    count_all = db.get_users_count()

    count_old = len(pay_guard.get_paid_more1_users())
    count_with_sub = base_statis.count_payments_dry()

    text = admin_users_msg(count_all, count_with_sub, count_old)
    keyboard = kb_admin_users()

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


def send_admin_payment(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    count_payments = base_statis.count_payments()
    summ_all_users = base_statis.summ_by_transactions()

    text = admin_main_statistics(count_payments, summ_all_users)
    keyboard = kb_statistics()

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


def send_admin_fut_posts(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    posts_count = len(db.get_all_posts())

    text = admin_fut_posts_msg(posts_count)
    keyboard = kb_posts()

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


def send_admin_params(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = menu_msg('Параметры')
    keyboard = kb_params()

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
        f'Тип: <b>{"Рекомендация" if post.details is None else "Пост"}</b>',
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

    bot.delete_state(user_id, chat_id)

    client = db.get_user_by_id(client_db_id)
    if client is None:
        return

    user_subsribe = db.get_current_subscribe_user(client_db_id)

    fin_date = 'нет'
    type_subscribe_show = ''

    if user_subsribe is not None:
        fin_date = get_str_by_datetime(user_subsribe.finish_dt)
        type_subscribe_show = f' тип {user_subsribe.product_type}'

    nikname = f'@{client.username}' if client.username != '' else ''
    count_ref = len(db.get_user_referals(client_db_id))
    is_banned = client.ban == 1

    text = '\n'.join((
        f'Пользователь <b>{nikname} | {client_db_id} {"(BAN)" if is_banned else ""}</b>',
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

    bot.delete_state(user_id, chat_id)

    text = menu_msg('Работники')
    keyboard = kb_admin_workers()

    if is_first:
        bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


def send_admin_workers_admin(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    res = '<b>Админы</b>\n'
    admins = db.get_admins()

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


def send_admin_workers_redactors(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    res = '<b>Редакторы</b>\n'
    redactors = db.get_redactors()

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


def send_admin_workers_support(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    sup = db.get_support_name()
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


def send_admin_tariffs(
    bot: TeleBot,
    message: Message,
    user_id: int,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = menu_msg('Тарифы')
    keyboard = kb_admin_tariffs()

    if is_first:
        bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


def send_admin_tariffs_list_item(
    bot: TeleBot,
    message: Message,
    user_id: int,
    page: int,
    type: Literal['default', 'delete', 'edit'] = 'default',
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    tariffs = db.get_prices()
    count = len(tariffs)

    if count == 0:
        bot.edit_message_text(
            'Тарифов нет', chat_id, mes_id,
            reply_markup=kb_admin_tariffs_back()
        )
    else:
        tariff = tariffs[page]

        text = msg_admin_tariff(tariff)
        image = tariff.img

        if type == 'delete':
            text += '\n\n⚠️<b>Удалить данный тарифы?</b>⚠️'
            keyboard = kb_admin_tariffs_delete(tariff.id or -1, page)
        elif type == 'edit':
            text += '\n\n<b>Что изменить?</b>'
            keyboard = kb_admin_tariffs_edit(tariff.id or -1, page)
        else:
            keyboard = kb_admin_tariffs_list(
                count, page, tariff.id or -1, tariff.switch_active == 1,
                tariff.discount is not None
            )

        def send():
            if image is None:
                bot.send_message(chat_id, text, reply_markup=keyboard)
            else:
                bot.send_photo(
                    chat_id, image, text,
                    reply_markup=keyboard
                )

        if is_first:
            send()
        elif message.content_type == 'photo' and image is not None:
            bot.edit_message_media(
                InputMediaPhoto(image, text, 'HTML'), chat_id, mes_id,
                reply_markup=keyboard
            )
        elif message.content_type == 'text' and image is None:
            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )
        else:
            delete_message(bot, chat_id, mes_id)
            send()
