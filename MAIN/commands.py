from telebot import TeleBot
from telebot.types import Message

from CALCULATE.callbacks.utils import send_calc_start
from db import db

from CALCULATE.callbacks import send_manual_page, send_settings
from CALCULATE.commands import _start as _calc
from CALCULATE.common.messages import msg_support
from MAIN.start import send_start_by_user
from MAIN.callbacks import send_site_code, kb_support

# from PIL import Image, ImageDraw, ImageFont
# from io import BytesIO
# import textwrap


def _start(message: Message, bot: TeleBot, data: dict):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_role: int = data.get('user_role') or 0
    has_registered_now: bool = data.get('has_registered_now') or False

    send_start_by_user(
        bot, message, user_id,
        user_role, has_registered_now,
    )


def _teststart(message: Message, bot: TeleBot, data: dict):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    db.set_calculator_user_market(user_db_id, 'crypto')

    send_start_by_user(
        bot, message, user_id,
        0, True,
    )


def _faq(message: Message, bot: TeleBot):
    text = db.get_text_by_name('FAQ')
    msg = text.message if (text is not None) else '*Ошибка*'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _about_us(message: Message, bot: TeleBot):
    text = db.get_text_by_name('О нас')
    msg = text.message if (text is not None) else '*Ошибка*'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _support(message: Message, bot: TeleBot):
    user_id = message.from_user.id

    sup = db.get_support_name()
    msg = msg_support(user_id)

    bot.send_message(
        message.chat.id, msg,
        reply_markup=kb_support(user_id, sup)
    )
    bot.delete_state(message.from_user.id, message.chat.id)


def _manual(message: Message, bot: TeleBot):
    send_manual_page(message, bot, 1, message.from_user.id, True)


def _site(message: Message, bot: TeleBot):
    send_site_code(bot, message, message.from_user.id, True)


def _settings(message: Message, bot: TeleBot):
    send_settings(bot, message, message.from_user.id, True)


def _calc_start(message: Message, bot: TeleBot):
    send_calc_start(bot, message, message.from_user.id)


def _test(message: Message, bot: TeleBot):
    print(message.chat.id)
    pass


def commands_registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(_teststart, commands=['teststart'])

    reg_mes(_start, commands=['start'])

    reg_mes(_faq, commands=['faq'])
    reg_mes(_about_us, commands=['about_us'])

    reg_mes(_support, commands=['support'])
    reg_mes(_support, commands=['team'])

    reg_mes(_manual, commands=['manual'])

    reg_mes(_calc, commands=['menu'])
    reg_mes(_settings, commands=['settings'])
    reg_mes(_calc_start, commands=['calc'])
    reg_mes(_calc_start, commands=['calculator'])
    # reg_mes(_site, commands=['site'])

    reg_mes(_test, commands=['test11'])
    bot.register_channel_post_handler(_test, pass_bot=True)
