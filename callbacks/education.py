from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from config_logger import logger
from db import db

from messages.education import curs_contents, curs, termins
from keyboards.education import (
    user_education_factory, UserEducationCallbackFilter,
    kb_user_lesson, kb_user_curs
)

from pages.user import send_user_main, send_user_terms, send_user_education


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot):
    callback_data = user_education_factory.parse(call.data)
    type = callback_data.get('type', '')
    page = int(callback_data.get('page', -1))
    num_les = int(callback_data.get('num_les', -1))

    user_id = call.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "user_education_factory" user_tg_id={user_id} type={type}')

    if type == 'back':
        await send_user_main(bot, call.message, user_id)

    if type == 'go_education':
        await send_user_education(bot, call.message, user_id)

    if 'terms' in type:
        if page == -1 or 'start' in type:
            page = 1
        elif 'prev' in type:
            page -= 1
        elif 'next' in type:
            page += 1
        elif 'end' in type:
            page = len(termins)

        if 'counter' not in type:
            await send_user_terms(bot, call.message, page, user_id)

    if 'curs' in type:
        count_now_les = db.get_lesson_count(user_db_id)
        if 'les' in type:
            if len(curs) + 1 == num_les:
                await bot.edit_message_text(
                    f'Доступные уроки закончились!\n{curs_contents}',
                    chat_id, mes_id, parse_mode='Markdown',
                    reply_markup=kb_user_curs(count_now_les)
                )
            else:
                lesson = curs[num_les - 1]

                if page == len(lesson) and count_now_les == num_les and count_now_les != len(curs):
                    db.add_lesson_count(user_db_id)

                await bot.edit_message_text(
                    lesson[page - 1], chat_id, mes_id,
                    parse_mode='Markdown',
                    reply_markup=kb_user_lesson(page, len(lesson), num_les)
                )
        elif 'counter' in type:
            pass
        else:
            await bot.edit_message_text(
                curs_contents, chat_id, mes_id,
                parse_mode='Markdown',
                reply_markup=kb_user_curs(count_now_les)
            )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(UserEducationCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore
        lambda _: True, pass_bot=True,
        user_education=user_education_factory.filter())
