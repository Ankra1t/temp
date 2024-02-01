from telebot import TeleBot
from telebot.types import Message

from config_logger import logger
from db import db
from db_new import db_new
from keyboard_reply import kb_user_sup

from CALCULATE.callbacks import send_manual_page, send_main
from MAIN.start import send_start_by_user


def _start(message: Message, bot: TeleBot, data: dict):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_role: int = data.get('user_role') or 0
    has_registered_now: bool = data.get('has_registered_now') or False

    send_start_by_user(
        bot, message, user_id, chat_id,
        user_role, has_registered_now,
    )


def _faq(message: Message, bot: TeleBot):
    logger.info(f'Запущена команда FAQ')

    msg = db.get_other_by_name('FAQ') or '*Ошибка*'
    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _about_us(message: Message, bot: TeleBot):
    logger.info(f'Запущена команда "О нас"')

    msg = db.get_other_by_name('О нас') or '*Ошибка*'
    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _support(message: Message, bot: TeleBot):
    sup = db_new.get_support_name()
    msg = 'Чтобы связаться с оператором тех.поддержки, нажмите на кнопку ниже👇'

    bot.send_message(message.chat.id, msg, reply_markup=kb_user_sup(sup))
    bot.delete_state(message.from_user.id, message.chat.id)


def _manual(message: Message, bot: TeleBot):
    send_manual_page(message, bot, 1, message.from_user.id, True)


def _calc(message: Message, bot: TeleBot):
    send_main(message, bot, message.from_user.id, True)


def commands_registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(_start, commands=['start'])
    reg_mes(_start, commands=['signals'])

    reg_mes(_faq, commands=['faq'])
    reg_mes(_about_us, commands=['about_us'])

    reg_mes(_support, commands=['support'])
    reg_mes(_support, commands=['team'])

    reg_mes(_manual, commands=['manual'])
    reg_mes(_calc, commands=['calc'])
