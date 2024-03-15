from datetime import datetime, timedelta

from telebot import TeleBot
from telebot.types import Message

from initialize import pay_guard, serv_tasks

from models import Update, Invoice, UpdateBBanker, InvoiceBBanker

from db_new import db_new
from keyboard_reply import kb_user_sup

from CALCULATE.callbacks import send_manual_page
from CALCULATE.commands import _start as _calc
from MAIN.start import send_start_by_user


from NOTIFIER import notifier
from NOTIFIER.messages import mess_set_trial_subsctibe_new_user
from messages.users import welcome_trial_subscribe_msg


def _start(message: Message, bot: TeleBot, data: dict):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_role: int = data.get('user_role') or 0
    has_registered_now: bool = data.get('has_registered_now') or False

    send_start_by_user(
        bot, message, user_id,
        user_role, has_registered_now,
    )


def _faq(message: Message, bot: TeleBot):
    text = db_new.get_text_by_name('FAQ')
    msg = text.message if (text is not None) else '*Ошибка*'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _about_us(message: Message, bot: TeleBot):
    text = db_new.get_text_by_name('О нас')
    msg = text.message if (text is not None) else '*Ошибка*'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _support(message: Message, bot: TeleBot):
    sup = db_new.get_support_name()
    msg = 'Чтобы связаться с оператором тех.поддержки, нажмите на кнопку ниже👇'

    bot.send_message(message.chat.id, msg, reply_markup=kb_user_sup(sup))
    bot.delete_state(message.from_user.id, message.chat.id)


def _manual(message: Message, bot: TeleBot):
    send_manual_page(message, bot, 1, message.from_user.id, True)


def _test(message: Message, bot: TeleBot):
    CHAT_KEY = -1002104767484
    chat = bot.get_chat(CHAT_KEY)
    print(chat.has_hidden_members)


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

    reg_mes(_test, commands=['test11'])

    bot.register_channel_post_handler(_test, pass_bot=True)
    bot.register_chat_member_handler(_test, pass_bot=True)
