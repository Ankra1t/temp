import re
from datetime import datetime
from typing import Any, Literal
from telebot import TeleBot
from telebot.types import Message
from BlockTGBotSender import BlockTGBotSender

from CALCULATE.common.messages import msg_digit_error
from MAIN.start import send_start_by_user
from MAIN.states import AdminPostsState
from MAIN.callbacks import kb_posts_back, kb_post_add_confirm, kb_post_confirm, send_admin_post, kb_posts
from MAIN.common.utils import get_post_from_message

from db import db
from common.utils import digit_accept, set_state_data, text_accept
from keyboard_reply import kb_live_cancel
from messages.workers import admin_fut_posts_msg
from models import Post, PostDetails


def handle_new_post_name(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        post: Post = data.get('post')
        kind: str = data.get('kind') or ''

    if kind == 'live':
        kb_cancel = kb_live_cancel()
    else:
        kb_cancel = kb_posts_back()

    name = text_accept(message)
    if name is None:
        bot.send_message(
            chat_id, 'Введите название текстом:',
            reply_markup=kb_cancel
        )
        return

    post.details = PostDetails(
        name=name,
        open_price=-1,
        stop_loss=-1
    )

    bot.set_state(user_id, AdminPostsState.signal_values, chat_id)
    set_state_data(bot, user_id, chat_id, {'post': post})
    bot.send_message(
        chat_id, 'Введите цену входа:',
        reply_markup=kb_cancel
    )


def handle_new_post_signal(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    with bot.retrieve_data(user_id, chat_id) as state_data:
        kind = state_data.get('kind') or ''
        post: Post = state_data.get('post')

    if post.details is None:
        print('ERROR["handle_new_post_signal"]: no details in post!')
        return

    if kind == 'live':
        kb_cancel = kb_live_cancel()
    else:
        kb_cancel = kb_posts_back()

    value = digit_accept(message)
    if (value is None) or (value <= 0):
        if post.details.open_price is None:
            text = 'Введите цену входа числом:'
        else:
            text = 'Введите стоп лосс числом:'

        bot.send_message(
            chat_id, text,
            reply_markup=kb_cancel
        )
        return

    if (post.details.open_price != -1) and (kind == 'live'):
        kind = 'signal'
        new_message = bot.send_message(chat_id, 'Отправка...')
        tg_sender = BlockTGBotSender(
            [], post.content, f'{post.media}({post.mes_type})',
            kind, post.details.open_price, value, post.details.name
        )
        tg_sender.send()

        bot.delete_state(user_id, chat_id)
        bot.edit_message_text('Успешно отправлен!', chat_id, new_message.id)
        return

    if post.details.open_price == -1:
        post.details.open_price = value
        state = AdminPostsState.signal_values
        text = 'Введите стоп лосс:'
    else:
        post.details.stop_loss = value
        state = AdminPostsState.datetime
        text = 'Введите дату и время в формате ДД* ММ* ГГ  ЧЧ* ММ*\nГде * - обязательные значения\nВведите "-", если хотите выложить прямо сейчас'

    bot.send_message(
        chat_id, text,
        reply_markup=kb_cancel
    )
    set_state_data(bot, user_id, chat_id, {'post': post})
    bot.set_state(user_id, state, chat_id)


def handle_new_post_content(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    post = get_post_from_message(bot, message)

    if post is None:
        bot.send_message(
            chat_id, 'Ошибка, попробуйте снова:',
            reply_markup=kb_posts_back()
        )
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        data['post'] = post
        kind = data.get('kind') or ''

    if kind == 'signal':
        state = AdminPostsState.name
        text = 'Введите название сигнала:'
    else:
        state = AdminPostsState.datetime
        text = 'Введите дату и время в формате ДД* ММ* ГГ  ЧЧ* ММ*\nГде * - обязательные значения\nВведите "-", если хотите выложить прямо сейчас'

    bot.send_message(
        chat_id, text,
        reply_markup=kb_posts_back()
    )
    bot.set_state(user_id, state, chat_id)


def handle_new_post_datetime(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    datetime_pattern = r'^(0?[1-9]|[1-2]\d|3[0-1])[ .]+(0?[1-9]|1[0-2])(?:[ .]+(\d{4}|\d{2}))?(?:[ ]+([0-1]?\d|2[0-3])[: ]+([0-5]?\d))?$'

    mes_text = text_accept(message) or '-'

    if mes_text != '-':
        value = re.search(datetime_pattern, mes_text)
        if value is None:
            bot.send_message(
                chat_id, 'Введите дату и время в формате ДД* ММ* ГГ  ЧЧ* ММ*\nГде * - обязательные значения\nВведите "-", если хотите выложить прямо сейчас',
                reply_markup=kb_posts_back())
            return

        day = int(value.group(1))
        month = int(value.group(2))
        year = value.group(3)
        if year is None:
            year = datetime.now().year
        elif len(year) == 2:
            year = int(f'20{year}')
        else:
            year = int(year)

        hour = int(value.group(4) or '0')
        minute = int(value.group(5) or '0')

        try:
            value = datetime(year, month, day, hour, minute)
        except:
            bot.send_message(
                chat_id, 'Неверная дата. Введите повторно ДД ММ (ГГ?) ЧЧ ММ',
                reply_markup=kb_posts_back())
            return
    else:
        value = datetime.now()

    with bot.retrieve_data(user_id, chat_id) as data:
        kind = data.get('kind')
        post: Post = data.get('post')
        post.date_time = value

    if post.details is None:
        details = (None, None, None)
    else:
        details = (
            post.details.open_price,
            post.details.stop_loss,
            post.details.name
        )

    if mes_text == '-':
        tg_sender = BlockTGBotSender(
            [], post.content, f'{post.media or ""}({post.mes_type})',
            kind, *details
        )
        tg_sender.send()
        bot.delete_state(user_id, chat_id)
        bot.send_message(
            chat_id, admin_fut_posts_msg(),
            reply_markup=kb_posts()
        )
    else:
        dt = post.date_time or datetime.now()
        send_admin_post(
            bot, chat_id, 0, f'{post.media or ""}({post.mes_type})',
            post.content, '-', dt.date(), dt.time().isoformat('minutes'), kind, *details
        )

        bot.set_state(user_id, AdminPostsState.confirm_add, chat_id)
        set_state_data(bot, user_id, chat_id, {'post': post})
        bot.send_message(
            chat_id, 'Выберите дейтсвие:',
            reply_markup=kb_post_add_confirm()
        )


def handle_action_post(action: Literal['send', 'delete']):
    def r_func(message: Message, bot: TeleBot):
        user_id = message.from_user.id
        chat_id = message.chat.id

        post_id = digit_accept(message, int)
        if post_id is None:
            bot.send_message(
                chat_id, msg_digit_error(user_id),
                reply_markup=kb_posts_back())
            return
        if not db.check_fut_post(post_id):
            bot.send_message(chat_id, f'Пост с ID: {post_id} - не существует!')
            bot.send_message(
                chat_id, 'Отправьте ID поста:',
                reply_markup=kb_posts_back())

        post: Any = db.get_fut_post(post_id)
        send_admin_post(bot, chat_id, *post)

        if action == 'delete':
            text = 'Удалить?'
        else:
            text = 'Отправить?'

        set_state_data(bot, user_id, chat_id, {'post_id': post_id})
        bot.set_state(user_id, AdminPostsState.comfirm_send_delete, chat_id)
        bot.send_message(
            chat_id, text,
            reply_markup=kb_post_confirm(action))

    return r_func


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_post_name, state=AdminPostsState.name)
    reg_mes(handle_new_post_signal, state=AdminPostsState.signal_values)

    reg_mes(handle_new_post_content, state=AdminPostsState.content)
    reg_mes(handle_new_post_datetime, state=AdminPostsState.datetime)

    reg_mes(handle_action_post('delete'), state=AdminPostsState.post_delete)
    reg_mes(handle_action_post('send'), state=AdminPostsState.post_send)
