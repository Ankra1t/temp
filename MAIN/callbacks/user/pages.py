from threading import Timer
from telebot import TeleBot
from telebot.types import Message, InputMediaPhoto

from db import db
from initialize import text_editor
from AuthRoles import get_site_code

from MAIN.common.messages import default_menu, msg_site_login, msg_user_tariff
from messages.education import termins
from messages.users import msg_choose_tariff_type, msg_start

from .main.keyboards import kb_site_login, kb_user_main
from .education.keyboards import kb_user_education, kb_user_pages
from .account.keyboards import kb_user_account
from .tariff.keyboards import kb_choose_products, kb_tariff_list, kb_user_tariff_back


def send_user_main(bot: TeleBot, message: Message, user_id: int, is_first=False, new_user=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    if not new_user and message.text is not None and len(message.text.split()) == 2:
        _, code = message.text.split()
        if code == 'site':
            send_site_code(bot, message, user_id, True)
            return

    if not new_user:
        text = text_editor.get_text(
            user_id, 'user_restart_bot'
        ) or msg_start(user_id)
    else:
        text = text_editor.get_text(user_id, 'welcome_user')

    keyboard = kb_user_main(user_id)

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
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    referals = db.get_user_referals(user_id)

    count_ref = len(referals)
    # TODO - добавить потраченные деньги и баланс пользователя
    money = 0
    balance = 0

    text = f'*Ваш баланс:* {balance}р.\n*Всего потратили:* {money}р.\n*У вас рефералов:* {count_ref}'
    keyboard = kb_user_account()

    if is_first:
        bot.send_message(
            user_id, text,
            parse_mode='Markdown', reply_markup=keyboard
        )
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            parse_mode='Markdown', reply_markup=keyboard
        )


def send_user_tariffs(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_choose_tariff_type(user_id)
    keyboard = kb_choose_products(user_id)

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
        print('[send_site_code]: сообщение не изменено!')

    if is_reset:
        code = new_code or ''

        def get_default():
            send_site_code(bot, new_message, user_id, False, False, code)

        Timer(3, get_default).start()


def send_tariffs_list_item(
    bot: TeleBot,
    message: Message,
    user_id: int,
    tariff_type: str,
    page: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    tariffs = db.get_prices_by_product(tariff_type, 1, 1)
    count = len(tariffs)

    if count == 0:
        bot.edit_message_text(
            'Тарифов нет', chat_id, mes_id,
            reply_markup=kb_user_tariff_back(user_id)
        )
    else:
        tariff = tariffs[page]
        tariff_id = tariff.id or 0

        image = tariff.img
        text = msg_user_tariff(user_id, tariff)
        keyboard = kb_tariff_list(user_id, tariff_id, count, tariff_type, page)

        def send():
            if image is None:
                bot.send_message(chat_id, text, reply_markup=keyboard)
            else:
                bot.send_photo(
                    chat_id, image, '',
                    reply_markup=keyboard
                )

        if is_first:
            send()
        elif message.content_type == 'photo' and image is not None:
            bot.edit_message_media(
                InputMediaPhoto(image, '', 'HTML'), chat_id, mes_id,
                reply_markup=keyboard
            )
        elif message.content_type == 'text' and image is None:
            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )
        else:
            bot.delete_message(chat_id, mes_id)
            send()
