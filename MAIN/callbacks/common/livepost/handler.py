from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db
from Classes.BlockTGBotSender import send_same_message_to_users

from states.admin_posts import AdminPostsState
from MAIN.callbacks import send_admin_main
from models import Post

from .filter import livepost_factory, LivepostCallbackFilter
from .keyboards import kb_livepost_cancel, kb_livepost_direction, kb_livepost_market, kb_livepost_time


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = livepost_factory.parse(call.data)
    call_type = data.get('type', '')
    value = data.get('value', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if call_type == 'cancel':
        bot.edit_message_text('Отменено!', chat_id, mes_id)
        send_admin_main(bot, call.message, user_id, True)

    if call_type == 'signal':
        bot.edit_message_text(
            'Введите название рекомендации:',
            chat_id, mes_id,
            reply_markup=kb_livepost_cancel()
        )
        bot.set_state(user_id, AdminPostsState.name, chat_id)

    if call_type == 'send_now':
        if value == '':
            bot.edit_message_text(
                'Кому отправить сообщение?',
                chat_id, mes_id,
                reply_markup=kb_livepost_direction()
            )
        elif value == 'time':
            bot.edit_message_text(
                'За какой период?', chat_id, mes_id,
                reply_markup=kb_livepost_time()
            )
        elif value == 'market':
            bot.edit_message_text(
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
                with bot.retrieve_data(user_id, chat_id) as data:
                    post: Post = data.get('post')
                    bot.edit_message_text('Отправка...', chat_id, mes_id)
                    send_same_message_to_users(
                        bot, users, post
                    )
                    bot.edit_message_text(
                        'Успешно отправлен!', chat_id, mes_id)
                    bot.delete_state(user_id, chat_id)
            else:
                bot.edit_message_text(
                    '❗️Таких пользователей нет.\nКому отправить сообщение?',
                    chat_id, mes_id,
                    reply_markup=kb_livepost_direction()
                )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(LivepostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        livepost=livepost_factory.filter()
    )
