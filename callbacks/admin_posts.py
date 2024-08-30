from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from Classes import pay_guard
from db import db
from common.utils import set_state_data
from models import Post


from keyboards.admin_posts import (
    admin_posts_factory, AdminPostsCallbackFilter,
    kb_post_kinds, kb_posts, kb_posts_back
)

from states.admin_posts import AdminPostsState
from pages.admin import send_admin_post, send_admin_fut_posts, send_admin_main


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot):
    callback_data: dict = admin_posts_factory.parse(call.data)
    type = callback_data['type']

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'go_main':
        await send_admin_main(bot, call.message, user_id)

    if type == 'go_posts':
        await send_admin_fut_posts(bot, call.message, user_id)

    if type == 'add':
        await bot.edit_message_text(
            'Выберите вид поста', chat_id, mes_id,
            reply_markup=kb_post_kinds()
        )

    if type == 'delete':
        await bot.edit_message_text(
            'Отправьте ID поста', chat_id, mes_id,
            reply_markup=kb_posts_back()
        )
        await bot.set_state(user_id, AdminPostsState.post_delete, chat_id)

    if type == 'list':
        posts = db.get_all_posts()

        if len(posts) == 0:
            await bot.edit_message_text(
                'Нет отложенных постов',
                chat_id, user_id,
                reply_markup=kb_posts()
            )
            return

        for i in range(len(posts)):
            await send_admin_post(bot, chat_id, posts[i])

        await send_admin_fut_posts(bot, call.message, user_id, True)

    if type == 'send_now':
        await bot.edit_message_text('Отправьте ID поста, чтобы его разослать сейчас',
                              chat_id, mes_id,
                              reply_markup=kb_posts_back())
        await bot.set_state(user_id, AdminPostsState.post_send, chat_id)

    if 'choose_kind_' in type:
        try:
            async with bot.retrieve_data(user_id, chat_id) as data:
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

        await bot.set_state(user_id, state, chat_id)
        await set_state_data(bot, user_id, chat_id, {'kind': kind})
        await bot.edit_message_text(
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

        async with bot.retrieve_data(user_id, chat_id) as data:
            post_data: Post = data.get('post')

        db.add_post(post_data)
        await bot.delete_state(user_id, chat_id)

        await bot.edit_message_text('Успешно!', chat_id, mes_id)
        await send_admin_fut_posts(bot, call.message, user_id, True)

    if 'confirm' in type:
        if 'no':
            await bot.edit_message_text(
                'Отправьте ID поста', chat_id, mes_id,
                reply_markup=kb_posts_back())
        if 'yes' in type:
            async with bot.retrieve_data(user_id, chat_id) as data:
                post_id = data.get('post_id', 0)
            text = 'Пост успешно удалён!'

            if 'send' in type:
                post = db.get_post(post_id)

                if post is None:
                    return

                if post.direct == 'Платным':
                    users = pay_guard.get_paid_users()
                elif post.direct == 'Бесплатным':
                    users = db.get_not_subscribed_users()
                else:
                    users = db.get_all_users()

                users_id = list(map(lambda user: user.tg_id, users))

                try:
                    pass
                    # tgsender = BlockTGBotSender(
                    #     users_id, post.content, post.media,
                    #     'post' if post.details is None else 'signal',
                    #     post.details.open_price, post.details.
                    # )

                    # tgsender.send()
                except Exception as e:
                    pass
                    #     (f'Ошибка рассылки постов в балансировщике при рассылке [{e}]')

                text = 'Пост успешно отправлен!'

            db.delete_post(post_id)

            await bot.delete_state(user_id, chat_id)
            await bot.edit_message_text(text, chat_id, mes_id)
            await send_admin_fut_posts(bot, call.message, user_id, True)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminPostsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore
        lambda _: True, pass_bot=True,
        admin_posts=admin_posts_factory.filter())
