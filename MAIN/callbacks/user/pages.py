from threading import Timer
from telebot import TeleBot
from telebot.types import Message

from CALCULATE.callbacks import kb_choose_lang
from CALCULATE.common.messages import msg_choose_lang
from Classes import text_editor
from AuthRoles import get_site_code
from common.utils import edit_message
from db import db
from data.data import liteDb

from config_logger import logger

from MAIN.common.messages import default_menu, msg_referral, msg_site_login, msg_user_account, msg_user_params
from messages.education import termins
from messages.users import msg_start

from .main.keyboards import kb_site_login, kb_user_main
from .education.keyboards import kb_user_education, kb_user_pages
from .account.keyboards import kb_user_account, kb_user_params, kb_user_referral


def send_user_main(bot: TeleBot, message: Message, user_id: int, is_first=False, new_user=False):
    # new_user=True
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    # if not new_user and message.text is not None and len(message.text.split()) == 2:
    #     _, code = message.text.split()
    #     if code == 'site':
    #         send_site_code(bot, message, user_id, True)
    #         return

    keyboard = kb_user_main(user_id, new_user)

    if not new_user:
        text = text_editor.get_text(
            user_id, 'user_restart_bot'
        ) or msg_start(user_id)

        if is_first:
            bot.send_message(
                chat_id, text,
                reply_markup=keyboard
            )
        else:
            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )

    else:
        bot.send_message(
            chat_id, msg_choose_lang(user_id),
            reply_markup=kb_choose_lang(user_id, True)
        )


def send_user_education(bot: TeleBot, message: Message, user_id: int):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    bot.edit_message_text(
        default_menu('Обучение'), chat_id, mes_id,
        reply_markup=kb_user_education()
    )


def send_user_terms(bot: TeleBot, message: Message, page: int, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    bot.edit_message_text(
        termins[page - 1], chat_id, mes_id, parse_mode='Markdown',
        reply_markup=kb_user_pages(page, len(termins))
    )


def send_user_account(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)
    liteDb.addPagesCount(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    referals = len(db.get_user_referals(user_db_id))

    purchase = db.get_purchases_by_user(user_db_id)
    money = 0
    for el in purchase:
        money += el.sum or 0

    text = msg_user_account(user_id, money, referals)
    keyboard = kb_user_account(user_id)

    if is_first:
        bot.send_message(
            user_id, text,
            reply_markup=keyboard
        )
    else:
        edit_message(
            bot, message, 'text', text, keyboard
        )


def send_site_code(bot: TeleBot, message: Message, user_id: int, is_first=False, is_reset=False, prev_code=''):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    new_code = prev_code or get_site_code(user_id)

    text = msg_site_login(user_id)
    keyboard = kb_site_login(user_id, new_code or '', is_reset)

    try:
        if is_first:
            new_message = bot.send_message(
                chat_id, text,
                reply_markup=keyboard
            )
        else:
            new_message = message
            bot.edit_message_text(
                text,
                chat_id, mes_id,
                reply_markup=keyboard
            )
    except:
        logger.error('[send_site_code]: сообщение не изменено!')

    if is_reset:
        code = new_code or ''

        def get_default():
            send_site_code(bot, new_message, user_id, False, False, code)

        Timer(3, get_default).start()


def send_referral(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    referals_count = len(db.get_user_referals(user_db_id))

    text = msg_referral(user_id, referals_count, bot.get_me().username)
    kb = kb_user_referral(user_id, referals_count)

    if is_first:
        bot.send_message(chat_id, text, reply_markup=kb)
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


def send_user_params(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    user = db.get_user_by_tg_id(user_id)
    liteDb.addPagesCount(user_id)

    if user is not None:
        text = msg_user_params(user_id, user)
        kb = kb_user_params(user_id)

        if is_first:
            bot.send_message(
                chat_id, text,
                reply_markup=kb
            )
        else:
            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb
            )
