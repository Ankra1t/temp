import re
from typing import Literal
from telebot.async_telebot import AsyncTeleBot

from db import db
from models import Post, PostDetails, Message, StateContext, User
from config_logger import logger
from common.utils import digit_accept, text_accept, get_post_from_message
from common.dt import get_datetime_by_str, get_datetime_now

from messages.errors import msg_digit_error
from states.admin_posts import AdminPostsState

from keyboards.admin_posts import kb_posts_back, kb_post_add_confirm, kb_post_confirm
from keyboards.livepost import (
    kb_livepost_cancel
)

from pages.admin import send_admin_post, send_admin_params

# TODO - удаляем

ticker_pattern = r'[a-zA-Z]+\/[a-zA-Z]+'


async def handle_new_post_name(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    async with state.data() as data:
        post: Post = data.get('post', {})
        kind: str = data.get('kind') or ''

    if kind == 'live':
        kb_cancel = kb_livepost_cancel()
    else:
        kb_cancel = kb_posts_back()

    name = text_accept(message)
    if name is None:
        await bot.send_message(
            chat_id, 'Введите название текстом:',
            reply_markup=kb_cancel
        )
        return

    ticker = re.search(ticker_pattern, post.content)
    if ticker is not None:
        ticker = ticker.group()

    post.details = PostDetails(
        name=name,
        open_price=-1,
        stop_loss=-1,
        ticker=(ticker or '').upper()
    )

    if ticker is None:
        text = 'Введите тикер (***/***):'
        new_state = AdminPostsState.ticker
    else:
        text = 'Введите цену входа:'
        new_state = AdminPostsState.signal_values

    await state.set(new_state)
    await state.add_data(post=post)
    await bot.send_message(
        chat_id, text,
        reply_markup=kb_cancel
    )


async def handle_new_post_ticker(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    async with state.data() as data:
        post: Post = data.get('post', {})
        kind: str = data.get('kind') or ''

    if kind == 'live':
        kb_cancel = kb_livepost_cancel()
    else:
        kb_cancel = kb_posts_back()

    ticker = text_accept(message)

    # if ticker is None or re.search(ticker_pattern, post.content) is None:
    if ticker is None:
        await bot.send_message(
            chat_id, 'Введите тикер текстом (***/***):',
            reply_markup=kb_cancel
        )
        return

    if post.details is not None:
        post.details.ticker = ticker.upper()

    await state.set(AdminPostsState.signal_values)
    await state.add_data(post=post)
    await bot.send_message(
        chat_id, 'Введите цену входа:',
        reply_markup=kb_cancel
    )


async def handle_new_post_signal(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    async with state.data() as state_data:
        kind = state_data.get('kind') or ''
        post: Post = state_data.get('post', {})

    if post.details is None:
        logger.error('[handle_new_post_signal]: no details in post!')
        return

    if kind == 'live':
        kb_cancel = kb_livepost_cancel()
    else:
        kb_cancel = kb_posts_back()

    value = digit_accept(message)
    if (value is None) or (value <= 0):
        if post.details.open_price is None:
            text = 'Введите цену входа числом:'
        else:
            text = 'Введите стоп-лосс числом:'

        await bot.send_message(
            chat_id, text,
            reply_markup=kb_cancel
        )
        return

    if (post.details.open_price != -1) and (kind == 'live'):
        post.details.stop_loss = value

        kind = 'signal'
        new_message = await bot.send_message(chat_id, 'Отправка...')

        await state.delete()
        await bot.edit_message_text('Успешно отправлен!', chat_id, new_message.id)
        return

    if post.details.open_price == -1:
        post.details.open_price = value
        new_state = AdminPostsState.signal_values
        text = 'Введите стоп-лосс:'
    else:
        post.details.stop_loss = value
        new_state = AdminPostsState.datetime
        text = 'Введите дату и время в формате ДД* ММ* ГГ  ЧЧ* ММ*\nГде * - обязательные значения\nВведите "-", если хотите выложить прямо сейчас'

    await bot.send_message(
        chat_id, text,
        reply_markup=kb_cancel
    )
    await state.add_data(post=post)
    await state.set(new_state)


async def handle_new_post_content(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    post = await get_post_from_message(bot, message, kb_posts_back)

    if post is None:
        await bot.send_message(
            chat_id, 'Ошибка, попробуйте снова:',
            reply_markup=kb_posts_back()
        )
        return

    async with state.data() as data:
        data['post'] = post
        kind = data.get('kind') or ''

    if kind == 'signal':
        new_state = AdminPostsState.name
        text = 'Введите название рекомендаций:'
    else:
        new_state = AdminPostsState.datetime
        text = 'Введите дату и время в формате ДД* ММ* ГГ  ЧЧ* ММ*\nГде * - обязательные значения\nВведите "-", если хотите выложить прямо сейчас'

    await bot.send_message(
        chat_id, text,
        reply_markup=kb_posts_back()
    )
    await state.set(new_state)


async def handle_new_post_datetime(message: Message, bot: AsyncTeleBot, state: StateContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    mes_text = text_accept(message) or '-'

    if mes_text != '-':
        value = get_datetime_by_str(mes_text)
        if value == False:
            await bot.send_message(
                chat_id, 'Введите дату и время в формате ДД.ММ.ГГ ЧЧ:ММ',
                reply_markup=kb_posts_back())
            return
    else:
        value = get_datetime_now()

    async with state.data() as data:
        kind = data.get('kind')
        post: Post = data.get('post', {})

    post.date_time = value

    if post.details is None:
        details = (None, None, None, None)
    else:
        details = (
            post.details.open_price,
            post.details.stop_loss,
            post.details.name,
            post.details.ticker
        )

    if mes_text == '-':
        await state.delete()
        await send_admin_params(bot, message, state, True)
    else:
        dt = post.date_time or get_datetime_now()
        await send_admin_post(bot, chat_id, post)

        await state.set(AdminPostsState.confirm_add)
        await state.add_data(post=post)
        await bot.send_message(
            chat_id, 'Выберите дейтсвие:',
            reply_markup=kb_post_add_confirm()
        )


async def handle_action_post(action: Literal['send', 'delete']):
    async def r_func(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
        chat_id = message.chat.id

        post_id = digit_accept(message, int)
        if post_id is None:
            await bot.send_message(
                chat_id, msg_digit_error(user.lang),
                reply_markup=kb_posts_back())
            return

        post = db.get_post(post_id)

        if post is None:
            await bot.send_message(chat_id, f'Пост с ID: {post_id} - не существует!')
            await bot.send_message(
                chat_id, 'Отправьте ID поста:',
                reply_markup=kb_posts_back()
            )
            return

        await send_admin_post(bot, chat_id, post)

        if action == 'delete':
            text = 'Удалить?'
        else:
            text = 'Отправить?'

        await state.add_data(post_id=post_id)
        await state.set(AdminPostsState.comfirm_send_delete)
        await bot.send_message(
            chat_id, text,
            reply_markup=kb_post_confirm(action)
        )

    return r_func


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_post_name, state=AdminPostsState.name)
    reg_mes(handle_new_post_ticker, state=AdminPostsState.ticker)
    reg_mes(handle_new_post_signal, state=AdminPostsState.signal_values)

    reg_mes(handle_new_post_content, state=AdminPostsState.content)
    reg_mes(handle_new_post_datetime, state=AdminPostsState.datetime)

    reg_mes(handle_action_post('delete'), state=AdminPostsState.post_delete)
    reg_mes(handle_action_post('send'), state=AdminPostsState.post_send)
