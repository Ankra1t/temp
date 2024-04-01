from telebot.types import Message, InputMediaPhoto
from telebot import TeleBot

from db import db
from initialize import pay_guard

from CALCULATE.common.messages import (
    msg_main, msg_main_freeze, msg_no_uses, msg_settings, msg_manual,
    msg_stats, msg_summury_profit_settings, msg_uses_count
)
from .manual.keyboards import kb_manual
from .main.keyboards import kb_main
from .settings.keyboards import kb_settings, kb_summury_profit
from .stats.keyboards import kb_stats


def send_main(message: Message, bot: TeleBot, user_id: int, is_first=False, is_new_calc=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    is_valid_use = pay_guard.valid_use_calc(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    uses_count = db.get_calculator_uses_count(user_db_id) or 0
    freeze_dt = db.get_user_calc_freeze(user_db_id)

    if is_valid_use:
        if is_new_calc:
            text = msg_uses_count(user_id, uses_count)
        else:
            text = msg_main(user_id, uses_count)
    elif freeze_dt is not None:
        text = msg_main_freeze(user_id, freeze_dt)
    else:
        text = msg_no_uses(user_id)

    keyboard = kb_main(user_id, is_valid_use, is_new_calc)

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


def send_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    msg = msg_settings(user_id)
    markup = kb_settings(user_id)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=markup
        )


def send_manual_page(message: Message, bot: TeleBot, page: int, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_manual[page - 1]
    photo = open(f'img\\info_calc\\{page}.jpg', 'rb')
    keyboard = kb_manual(user_id, page, len(msg_manual))

    if is_first:
        bot.send_photo(
            chat_id, photo, text, 'MarkDown',
            reply_markup=keyboard
        )
    else:
        bot.edit_message_media(
            InputMediaPhoto(photo, text, 'MarkDown'),
            chat_id, mes_id,
            reply_markup=keyboard
        )


def send_summury_profit_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_summury_profit_settings(user_id)
    kb = kb_summury_profit(user_id)

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


def send_stats(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_stats(user_id)
    kb = kb_stats(user_id)

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
