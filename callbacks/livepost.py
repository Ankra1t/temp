from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import CallbackQuery, StateContext

from states.admin_posts import AdminPostsState
from keyboards.livepost import (
    livepost_factory, LivepostCallbackFilter,
    kb_livepost_cancel, kb_livepost_direction,
    kb_livepost_market, kb_livepost_time
)
from pages.admin import send_admin_main

# TODO - удалить модуль livepost


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
                # TODO - Добавить получение пользователей тг
                users = []
            elif value == 'paid':
                # TODO - Добавить получение пользователей с подпиской
                users = []
            elif value in ('RF', 'USA', 'crypto', 'forex'):
                # TODO - Добавить получение пользователей по рынку. Возможно удалить
                users = []
            elif value in ('2h', '6h', '12h', '24h'):
                # TODO - Добавить получение пользователей зарегистрированных за последние часы
                users = []

            if len(users) != 0:
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
