from telebot import TeleBot
from telebot.types import Message
from telebot.util import extract_arguments


from config_logger import logger
from AuthRoles import check_registrate
from NOTIFIER import notifier
from db import db
from messages.main import msg_support
from models import LANGUAGES
from services import auth

from common.utils import get_lang, is_digit
from common.calc_step import send_calc_start

from pages.calculate import send_admin_channel_calc_list, send_channel_post, send_main, send_manual_page, send_settings
from pages.user import send_referral, send_site_code
from pages.start import send_start_by_user

from keyboards.account import kb_support


def _start(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_role = check_registrate(user_id)
    is_registered = False

    if user_role is None:
        # Проверяем реферальный id
        mes_args = extract_arguments(message.text or '')

        ref_id = None
        if mes_args is not None and is_digit(mes_args):
            ref_id = int(mes_args)

        username = message.from_user.username

        is_registered = auth.registration(user_id, username, ref_id)
        new_user = db.get_user_by_tg_id(user_id)

        if new_user is not None and is_registered == True:
            logger.info(
                f'/auth/tg_register [tg_id={user_id} @{username}]'
            )

            num = len(db.get_today_users())

            # Проверка языка
            user_lang = (message.from_user.language_code or 'en').lower()
            lang = user_lang if (user_lang in LANGUAGES) else 'en'
            db.set_user_lang(new_user.id, lang)

            # Уведомление о регистрации
            sentMessages = notifier.send_user_is_registered(
                new_user.id, user_lang, num
            )

            if sentMessages:
                auth.addUserNotificationMessages(
                    new_user.id, sentMessages, user_lang, num
                )

            is_registered = True
        else:
            logger.error(
                f'Ошибка регистрации пользователя tg_id={user_id} @{username}'
            )

    send_start_by_user(
        bot, message, user_id,
        user_role or 0, is_registered or False,
    )


def _calc(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    send_main(message, bot, user_id, True)
    bot.delete_state(user_id, chat_id)


def _teststart(message: Message, bot: TeleBot):
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
    lang = get_lang(user_id)

    sup = db.get_support_name()
    msg = msg_support(lang)

    bot.send_message(
        message.chat.id, msg,
        reply_markup=kb_support(lang, sup)
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


def _channel_calc(message: Message, bot: TeleBot):
    user_db_id = db.get_user_id_by_tg_id(message.from_user.id)
    isAdmin = db.get_worker_role(user_db_id)

    if not isAdmin:
        return

    send_calc_start(bot, message, message.from_user.id, is_channel_calc=True)


def _referral(message: Message, bot: TeleBot):
    send_referral(bot, message, message.from_user.id, True)


def _channel_post(message: Message, bot: TeleBot):
    user_db_id = db.get_user_id_by_tg_id(message.from_user.id)
    admin = db.get_worker_role(user_db_id)
    if admin is None:
        return

    send_channel_post(bot, message, message.from_user.id, True)


def _results(message: Message, bot: TeleBot):
    user_db_id = db.get_user_id_by_tg_id(message.from_user.id)
    admin = db.get_worker_role(user_db_id)
    if admin is None:
        return

    send_admin_channel_calc_list(bot, message, message.from_user.id, True)


def _test(message: Message, bot: TeleBot):
    print(message.chat.id)


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
    reg_mes(_channel_calc, commands=['channel_calc'])

    reg_mes(_channel_post, commands=['channels'])
    reg_mes(_results, commands=['d'])

    reg_mes(_referral, commands=['referral'])

    reg_mes(_test, commands=['test11'])

    bot.register_channel_post_handler(_test, pass_bot=True)
