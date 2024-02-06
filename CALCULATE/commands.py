from telebot import TeleBot
from telebot.types import Message
from CALCULATE.callbacks.settings.keyboards import kb_settings_confirm

from db import db
from db_new import db_new

from CALCULATE.common.messages import msg_support, msg_welcome
from CALCULATE.common.keyboard import kb_support
from CALCULATE.callbacks import send_manual_page, send_main


def _start(message: Message, bot: TeleBot, data: dict):
    user_id = message.from_user.id
    chat_id = message.chat.id

    has_registered_now = data.get('has_registered_now')

    if has_registered_now:
        bot.send_message(
            chat_id, msg_welcome(user_id),
            reply_markup=kb_settings_confirm(user_id, 'welcome')
        )
    else:
        send_main(message, bot, user_id, True)

    bot.clear_step_handler(message)
    bot.delete_state(user_id, chat_id)


def _faq(message: Message, bot: TeleBot):
    text = db_new.get_text_by_name('FAQ')
    msg = text.message if (text is not None) else 'Ошибка'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _about_us(message: Message, bot: TeleBot):
    text = db_new.get_text_by_name('О нас')
    msg = text.message if (text is not None) else 'Ошибка'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _support(message: Message, bot: TeleBot):
    sup = db_new.get_support_name()
    bot.send_message(
        message.chat.id, msg_support(message.from_user.id),
        reply_markup=kb_support(message.from_user.id, sup)
    )


def _manual(message: Message, bot: TeleBot):
    send_manual_page(message, bot, 1, message.from_user.id, True)


def commands_registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(_start, commands=['start'])
    reg_mes(_start, commands=['calc'])

    reg_mes(_faq, commands=['faq'])
    reg_mes(_about_us, commands=['about_us'])

    reg_mes(_support, commands=['support'])
    reg_mes(_support, commands=['team'])

    reg_mes(_manual, commands=['manual'])
