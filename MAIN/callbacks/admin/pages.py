from telebot import TeleBot
from telebot.types import Message

from db import db
from initialize import pay_guard

from MAIN.common.utils import get_print_signal_info
from common.vars import PRINT_DATE_FROMAT
from models import Post, User
from .users.keyboards import kb_admin_client_info


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
        f'Дата и время поста: <b>{post.date_time.strftime(PRINT_DATE_FROMAT)}</b>\n' if post.date_time is not None else ''
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


def send_admin_client(bot: TeleBot, message: Message, user_id: int, client_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    user = db.get_user_by_id(client_id)
    if user is None:
        return

    user_check = User()
    user_check.id = user[9]
    user_subsriber = pay_guard.get_current_subscribe_user(user_check)

    fin_date = 'нет'
    type_subscribe_show = ''

    if user_subsriber.subscribe is not None:
        fin_date = user_subsriber.subscribe.finish_dt.strftime(
            '%d/%m/%Y')
        type_subscribe_show = f' тип {user_subsriber.subscribe.type}'

    count_ref = len(db.get_referals(user_id))
    is_banned = user[10] is not None

    text = '\n'.join((
        f'Пользователь <b>@{user[2]} | {user[9]} {"(BAN)" if is_banned else ""}</b>',
        f'Подписка: {fin_date}{type_subscribe_show}',
        f'Баланс: <b>{user[7]}</b>',
        f'Рефералов: <b>{count_ref}</b>',
        '',
        '<b>Выберите действие 👇</b>'
    ))

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=kb_admin_client_info(client_id, is_banned)
        )
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_admin_client_info(client_id, is_banned)
        )
