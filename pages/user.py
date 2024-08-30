from threading import Timer
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from Classes import text_editor
from common.utils import edit_message, get_lang
from db import db
from data.data import liteDb
from services import auth
from config_logger import logger

from messages.education import termins
from messages.enter import msg_choose_lang
from messages.profile import msg_referral, msg_site_login, msg_user_account, msg_user_params
from messages.users import msg_start

from keyboards.settings import kb_choose_lang
from keyboards.account import kb_user_account, kb_user_params, kb_user_referral
from keyboards.education import kb_user_education, kb_user_pages
from keyboards.user_main import kb_site_login, kb_user_main


async def send_user_main(bot: AsyncTeleBot, message: Message, user_id: int, is_first=False, new_user=False):
    # new_user=True
    chat_id = message.chat.id
    mes_id = message.id

    lang = get_lang(user_id)

    await bot.delete_state(user_id, chat_id)

    # if not new_user and message.text is not None and len(message.text.split()) == 2:
    #     _, code = message.text.split()
    #     if code == 'site':
    #         send_site_code(bot, message, user_id, True)
    #         return

    keyboard = kb_user_main(lang, new_user)

    if not new_user:
        text = text_editor.get_text(
            user_id, 'user_restart_bot'
        ) or msg_start(user_id)

        if is_first:
            await bot.send_message(
                chat_id, text,
                reply_markup=keyboard
            )
        else:
            await bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )

    else:
        await bot.send_message(
            chat_id, msg_choose_lang(lang),
            reply_markup=kb_choose_lang(lang, True)
        )


async def send_user_education(bot: AsyncTeleBot, message: Message, user_id: int):
    chat_id = message.chat.id
    mes_id = message.id

    await bot.delete_state(user_id, chat_id)

    await bot.edit_message_text(
        'Обучение', chat_id, mes_id,
        reply_markup=kb_user_education()
    )


async def send_user_terms(bot: AsyncTeleBot, message: Message, page: int, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    await bot.delete_state(user_id, chat_id)

    await bot.edit_message_text(
        termins[page - 1], chat_id, mes_id, parse_mode='Markdown',
        reply_markup=kb_user_pages(page, len(termins))
    )


async def send_user_account(bot: AsyncTeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    await bot.delete_state(user_id, chat_id)
    liteDb.addPagesCount(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)
    referals = len(db.get_user_referals(user_db_id))

    purchase = db.get_purchases_by_user(user_db_id)
    money = 0
    for el in purchase:
        money += el.sum or 0

    text = msg_user_account(lang, money, referals)
    keyboard = kb_user_account(lang, user_id)

    if is_first:
        await bot.send_message(
            user_id, text,
            reply_markup=keyboard
        )
    else:
        await edit_message(
            bot, message, 'text', text, keyboard
        )


async def send_site_code(bot: AsyncTeleBot, message: Message, user_id: int, is_first=False, is_reset=False, prev_code=''):
    chat_id = message.chat.id
    mes_id = message.id

    lang = get_lang(user_id)
    user_db_id = db.get_user_id_by_tg_id(user_id)

    await bot.delete_state(user_id, chat_id)

    new_code = prev_code or auth.get_site_code(user_db_id)

    text = msg_site_login(lang)
    keyboard = kb_site_login(lang, new_code or '', is_reset)

    try:
        if is_first:
            new_message = await bot.send_message(
                chat_id, text,
                reply_markup=keyboard
            )
        else:
            new_message = message
            await bot.edit_message_text(
                text,
                chat_id, mes_id,
                reply_markup=keyboard
            )
    except:
        logger.error('[send_site_code]: сообщение не изменено!')

    if is_reset:
        code = new_code or ''

        async def get_default():
            await send_site_code(bot, new_message, user_id, False, False, code)

        Timer(3, get_default).start()


async def send_referral(bot: AsyncTeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)
    referals_count = len(db.get_user_referals(user_db_id))

    text = msg_referral(lang, referals_count, (await bot.get_me()).username, user_db_id)
    kb = kb_user_referral(lang, referals_count)

    if is_first:
        await bot.send_message(chat_id, text, reply_markup=kb)
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


async def send_user_params(bot: AsyncTeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    lang = get_lang(user_id)
    user = db.get_user_by_tg_id(user_id)
    liteDb.addPagesCount(user_id)

    if user is not None:
        text = msg_user_params(lang, user)
        kb = kb_user_params(lang)

        if is_first:
            await bot.send_message(
                chat_id, text,
                reply_markup=kb
            )
        else:
            await bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb
            )
