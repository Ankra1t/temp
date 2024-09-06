from threading import Timer
from telebot.async_telebot import AsyncTeleBot

from common.utils import edit_message
from db import db
from data.data import liteDb
from services import auth
from config_logger import logger
from models import Message, StateContext, User

from messages.education import termins
from messages.enter import msg_choose_lang
from messages.profile import msg_referral, msg_site_login, msg_user_account, msg_user_params
from messages.users import msg_start

from keyboards.settings import kb_choose_lang
from keyboards.account import kb_user_account, kb_user_params, kb_user_referral
from keyboards.education import kb_user_education, kb_user_pages
from keyboards.user_main import kb_site_login, kb_user_main


async def send_user_main(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    new_user=False,
    is_first=False,
):
    # new_user=True
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    # if not new_user and message.text is not None and len(message.text.split()) == 2:
    #     _, code = message.text.split()
    #     if code == 'site':
    #         send_site_code(bot, message, user_id, True)
    #         return

    keyboard = kb_user_main(user.lang, new_user)

    if not new_user:
        text = msg_start(user.lang)

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
            chat_id, msg_choose_lang(user.lang),
            reply_markup=kb_choose_lang(user.lang, True)
        )


async def send_user_education(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    await bot.edit_message_text(
        'Обучение', chat_id, mes_id,
        reply_markup=kb_user_education()
    )


async def send_user_terms(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    page: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    await bot.edit_message_text(
        termins[page - 1], chat_id, mes_id, parse_mode='Markdown',
        reply_markup=kb_user_pages(page, len(termins))
    )


async def send_user_account(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False,
):
    chat_id = message.chat.id

    await state.delete()
    liteDb.addPagesCount(user.tgId)

    referals = len(db.get_user_referals(user.id))

    purchase = db.get_purchases_by_user(user.id)
    money = 0
    for el in purchase:
        money += el.sum or 0

    text = msg_user_account(user.lang, money, referals)
    keyboard = kb_user_account(user.lang, user.tgId)

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await edit_message(
            bot, message, 'text', text, keyboard
        )


async def send_site_code(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_reset=False,
    prev_code='',
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    new_code = prev_code or auth.get_site_code(user.id)

    text = msg_site_login(user.lang)
    keyboard = kb_site_login(user.lang, new_code or '', is_reset)

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

        if is_reset:
            code = new_code or ''

            async def get_default():
                await send_site_code(
                    bot, new_message, state, user,  # type: ignore
                    False, code, False,
                )

            Timer(3, get_default).start()
    except:
        logger.error('[send_site_code]: сообщение не изменено!')


async def send_referral(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    referals_count = len(db.get_user_referals(user.id))

    text = msg_referral(user.lang, referals_count, (await bot.get_me()).username or '', user.id)
    kb = kb_user_referral(user.lang, referals_count)

    if is_first:
        await bot.send_message(chat_id, text, reply_markup=kb)
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


async def send_user_params(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    liteDb.addPagesCount(user.tgId)
    user_info = db.get_user_by_id(user.id)

    if user_info is not None:
        text = msg_user_params(user.lang, user_info)
        kb = kb_user_params(user.lang)

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
