from typing import Any
from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db
from BlockTGBotSender import BlockTGBotSender
from MAIN.callbacks import send_admin_post
from MAIN.states import AdminPostsState
from messages.workers import admin_fut_posts_msg
from common.utils import set_state_data
from models import Post

from .keyboards import kb_post_kinds, kb_posts, kb_posts_back
from .filter import admin_posts_factory, AdminPostsCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = admin_posts_factory.parse(call.data)
    type = callback_data['type']

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'add':
        bot.edit_message_text(
            'Выберите вид поста', chat_id, mes_id,
            reply_markup=kb_post_kinds()
        )

    if type == 'delete':
        bot.edit_message_text(
            'Отправьте ID поста', chat_id, mes_id,
            reply_markup=kb_posts_back()
        )
        bot.set_state(user_id, AdminPostsState.post_delete, chat_id)

    if type == 'list':
        posts = db.get_fut_all_posts()

        if len(posts) != 0:
            for i in range(len(posts)):
                send_admin_post(bot, chat_id, posts[i])
            text = admin_fut_posts_msg()
        else:
            text = 'Нет отложенных постов'

        bot.send_message(
            chat_id, text,
            reply_markup=kb_posts()
        )

    if type == 'send_now':
        bot.edit_message_text('Отправьте ID поста, чтобы его разослать сейчас',
                              chat_id, mes_id,
                              reply_markup=kb_posts_back())
        bot.set_state(user_id, AdminPostsState.post_send, chat_id)

    if 'choose_kind_' in type:
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                prev_kind = data.get('kind') or ''
        except:
            prev_kind = ''

        if 'signal' in type:
            kind = 'signal'
        else:
            kind = 'post'

        text = 'Отправьте отложенный пост:'
        state = AdminPostsState.content

        if prev_kind == 'live':
            if kind == 'signal':
                state = AdminPostsState.signal_values
                text = 'Введите цену входа:'
            else:
                state = AdminPostsState.datetime
                text = 'Введите дату и время в формате ДД* ММ* ГГ  ЧЧ* ММ*\nГде * - обязательные значения\nВведите "-", если хотите выложить прямо сейчас'

        bot.set_state(user_id, state, chat_id)
        set_state_data(bot, user_id, chat_id, {'kind': kind})
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_posts_back()
        )

    if 'add_' in type:
        if 'private' in type:
            type = 'Платный'
        elif 'public' in type:
            type = 'Бесплатный'
        else:
            type = 'Всем'

        with bot.retrieve_data(user_id, chat_id) as data:
            kind = data.get('kind')
            post_data: Post = data.get('post')

        db.add_fut_post(post_data, kind)
        bot.delete_state(user_id, chat_id)

        bot.edit_message_text('Успешно!', chat_id, mes_id)
        bot.send_message(
            chat_id, admin_fut_posts_msg(),
            reply_markup=kb_posts()
        )

    if 'confirm' in type:
        if 'no':
            bot.edit_message_text(
                'Отправьте ID поста', chat_id, mes_id,
                reply_markup=kb_posts_back())
        if 'yes' in type:
            with bot.retrieve_data(user_id, chat_id) as data:
                post_id = data.get('post_id')
            text = 'Пост успешно удалён!'

            if 'send' in type:
                post = db.get_fut_post(post_id)

                if post is None:
                    return

                if post.direct == 'Платным':
                    users = db.get_users_with_sub()
                elif post.direct == 'Бесплатным':
                    users = db.get_users_without_sub()
                else:
                    users = db.get_all_users()

                users_id = list(map(lambda user: user[9], users))

                try:
                    pass
                    # tgsender = BlockTGBotSender(
                    #     users_id, post.content, post.media,
                    #     'post' if post.details is None else 'signal',
                    #     post.details.open_price, post.details.
                    # )

                    # tgsender.send()
                except Exception as e:
                    print(f'Ошибка рассылки постов в балансировщике при рассылке [{e}]')

                text = 'Пост успешно отправлен!'

            db.del_fut_post(post_id)

            bot.delete_state(user_id, chat_id)
            bot.edit_message_text(text, chat_id, mes_id)
            bot.send_message(
                chat_id, admin_fut_posts_msg(),
                reply_markup=kb_posts(),
                parse_mode='HTML')

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminPostsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_posts=admin_posts_factory.filter())
