from telebot import TeleBot
from telebot.types import Message

from db import db
from db_new import db_new
from initialize import text_editor

from MAIN.common.messages import default_menu
from messages.education import termins
from .main.keyboards import kb_user_main
from .education.keyboards import kb_user_education, kb_user_pages
from .account.keyboards import kb_user_account


def send_user_main(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    text = text_editor.get_text('welcome_user')
    keyboard = kb_user_main()

    bot.delete_state(user_id, chat_id)

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

    referals = db_new.get_user_referals(user_id)

    count_ref = len(referals)
    money = db.get_pay_money(user_id)
    balance = db.get_balance(user_id)

    bot.delete_state(user_id, chat_id)

    bot.send_message(
        user_id,
        f'*Ваш баланс:* {balance}р.\n*Всего потратили:* {money}р.\n*У вас рефералов:* {count_ref}',
        parse_mode='Markdown', reply_markup=kb_user_account()
    )


def send_user_tariffs(bot: TeleBot, message: Message, user_id: int):

    pass
