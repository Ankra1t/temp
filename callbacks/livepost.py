from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from db import db
from models import Post, CallbackQuery, StateContext

from states.admin_posts import AdminPostsState
from keyboards.livepost import (
    livepost_factory, LivepostCallbackFilter,
    kb_livepost_cancel, kb_livepost_direction,
    kb_livepost_market, kb_livepost_time
)
from pages.admin import send_admin_main

# TODO - Удалить livepost


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    data = livepost_factory.parse(call.data)
    call_type = data.get('type', '')
    value = data.get('value', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if call_type == 'cancel':
        await bot.edit_message_text('Отменено!', chat_id, mes_id)
        await send_admin_main(bot, call.message, state, True)

    if call_type == 'signal':
        await bot.edit_message_text(
            'Введите название рекомендации:',
            chat_id, mes_id,
            reply_markup=kb_livepost_cancel()
        )
        await state.set(AdminPostsState.name)

    if call_type == 'send_now':
        if value == '':
            await bot.edit_message_text(
                'Кому отправить сообщение?',
                chat_id, mes_id,
                reply_markup=kb_livepost_direction()
            )
        elif value == 'time':
            await bot.edit_message_text(
                'За какой период?', chat_id, mes_id,
                reply_markup=kb_livepost_time()
            )
        elif value == 'market':
            await bot.edit_message_text(
                'Для какого рынка?', chat_id, mes_id,
                reply_markup=kb_livepost_market()
            )
        else:
            users = []
            if value == 'all':
                users = db.get_all_users()
            elif value == 'paid':
                users = db.get_subsribed_users()
            elif value in ('RF', 'USA', 'crypto', 'forex'):
                users = db.get_paginated_users(market_filter=value)
            elif value in ('2h', '6h', '12h', '24h'):
                users = db.get_users_created_in_last(
                    int(value.replace('h', '')))

            if len(users) != 0:
                async with state.data() as data:
                    post: Post = data.get('post', {})

                await bot.edit_message_text('Отправка...', chat_id, mes_id)
                await bot.edit_message_text(
                    'Успешно отправлен!', chat_id, mes_id)
                await state.delete()
            else:
                await bot.edit_message_text(
                    '❗️Таких пользователей нет.\nКому отправить сообщение?',
                    chat_id, mes_id,
                    reply_markup=kb_livepost_direction()
                )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(LivepostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        livepost=livepost_factory.filter()
    )
