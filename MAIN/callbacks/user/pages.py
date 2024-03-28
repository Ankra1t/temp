from threading import Timer
from telebot import TeleBot
from telebot.types import Message

from db_new import db_new
from initialize import text_editor
from AuthRoles import get_site_code

from MAIN.common.messages import default_menu, msg_site_login
from messages.education import termins
from .main.keyboards import kb_site_login, kb_user_main
from .education.keyboards import kb_user_education, kb_user_pages
from .account.keyboards import kb_user_account


def send_user_main(bot: TeleBot, message: Message, user_id: int, is_first=False, new_user=False):
    chat_id = message.chat.id
    mes_id = message.id

    if not new_user and message.text is not None and len(message.text.split()) == 2:
        _, code = message.text.split()
        if code == 'site':
            send_site_code(bot, message, user_id, True)
            return

    text = text_editor.get_text('welcome_user')
    if not new_user:
        text = text_editor.get_text(
            'user_restart_bot'
        ) or 'Доброго времени. Выберите действие'

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
    # TODO - добавить потраченные деньги и баланс пользователя
    money = 0
    balance = 0

    bot.delete_state(user_id, chat_id)

    bot.send_message(
        user_id,
        f'*Ваш баланс:* {balance}р.\n*Всего потратили:* {money}р.\n*У вас рефералов:* {count_ref}',
        parse_mode='Markdown', reply_markup=kb_user_account()
    )


def send_user_tariffs(bot: TeleBot, message: Message, user_id: int):

    pass


def send_site_code(bot: TeleBot, message: Message, user_id: int, is_first=False, is_reset=False, prev_code=''):
    chat_id = message.chat.id
    mes_id = message.id

    new_code = prev_code or get_site_code(user_id)

    text = msg_site_login()
    keyboard = kb_site_login(new_code or '', is_reset)

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
        print('[send_site_code]: сообщение не изменено!')

    if is_reset:
        code = new_code or ''

        def get_default():
            send_site_code(bot, new_message, user_id, False, False, code)

        Timer(3, get_default).start()
