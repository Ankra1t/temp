from telebot.types import Message, InputMediaPhoto
from telebot import TeleBot

from db_new import db_new
from initialize import pay_guard

from CALCULATE.common.messages import msg_main, msg_no_uses, msg_settings, msg_manual
from .manual.keyboards import kb_manual
from .main.keyboards import kb_main
from .settings.keyboards import kb_settings


def send_main(message: Message, bot: TeleBot, user_id: int, is_first=False):
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    uses_count = db_new.get_calculator_uses_count(user_db_id) or 0

    if pay_guard.valid_use_calc(user_id):
        text = msg_main(user_id, uses_count)
        keyboard = kb_main(user_id)
    else:
        text = msg_no_uses(user_id)
        keyboard = kb_main(user_id, False)

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

    msg = msg_settings(user_id)
    markup = kb_settings(user_id)

    bot.delete_state(user_id, chat_id)

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

    text = msg_manual[page - 1]
    photo = open(f'img\\info_calc\\{page}.jpg', 'rb')
    keyboard = kb_manual(user_id, page, len(msg_manual))

    bot.delete_state(user_id, chat_id)

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
