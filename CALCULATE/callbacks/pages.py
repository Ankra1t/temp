import os
from telebot.types import Message, InputMediaPhoto
from telebot import TeleBot

from MAIN.common.messages import msg_user_tariff
from common.utils import delete_message, edit_message, get_lang, set_state_data
from db import db

from Classes import pay_guard, calcService, hti
from CALCULATE.states import StatsState
from CALCULATE.common.messages import (
    msg_calculation, msg_deposit,
    msg_freeze_calc, msg_main, msg_main_freeze,
    msg_no_uses, msg_settings, msg_manual,
    msg_stats_page, msg_summury_profit_settings
)

from messages.users import msg_choose_tariff_type, msg_no_tariffs
from models import MARKETS_TYPE, Calculation

from .manual.keyboards import kb_manual
from .main.keyboards import kb_main
from .settings.keyboards import kb_change_deposit, kb_first_calc_info, kb_settings, kb_summury_profit
from .stats.keyboards import kb_freeze_calc, kb_stats
from .tariff.keyboards import kb_choose_products, kb_tariff_list, kb_user_tariff_back


def send_main(message: Message, bot: TeleBot, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    is_rus = bot.get_chat_member(chat_id, user_id).user.language_code == 'ru'
    is_valid_use = pay_guard.valid_use_calc(user_id, bot)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    uses_count = db.get_calculator_uses_count(user_db_id) or 0
    freeze_dt = db.get_user_calc_freeze(user_db_id)
    unfinished_calc = db.get_unfinished_calc_by_user(user_db_id)

    if is_valid_use:
        text = msg_main(user_id, uses_count, is_rus)
    elif freeze_dt is not None:
        text = msg_main_freeze(user_id, freeze_dt)
    else:
        text = msg_no_uses(user_id)

    keyboard = kb_main(user_id, is_valid_use, None,
                       unfinished_calc is not None)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        edit_message(
            bot, message, 'text', text, keyboard
        )


def send_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calc_output = db.get_user_calc_output(user_db_id)

    msg = msg_settings(user_id)
    markup = kb_settings(user_id, calc_output)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        edit_message(bot, message, 'text', msg, markup)


def send_user_deposit(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    market = db.get_user_current_market(user_db_id)
    u_base = db.get_calc_user_settings(user_db_id)

    is_update = False
    if u_base is not None:
        is_update = u_base.is_updating_deposit

    text = msg_deposit(user_id)
    keyboard = kb_change_deposit(user_id, is_update, market)

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


def send_manual_page(message: Message, bot: TeleBot, page: int, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_manual[page - 1]
    photo = open(f'src/img/info_calc/{page}.jpg', 'rb')
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

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calcs = db.get_calculations_by_user(user_db_id)

    text = msg_stats_page(user_id, len(calcs))
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
        edit_message(
            bot, message, 'text', text, keyboard
        )


def send_tariffs_list_item(
    bot: TeleBot,
    message: Message,
    user_id: int,
    tariff_type: str,
    page: int,
    is_first=False,
    is_rus=False
):
    chat_id = message.chat.id
    mes_id = message.id

    tariffs = db.get_prices_by_product(tariff_type, 1, 1)
    count = len(tariffs)

    if count == 0:
        bot.edit_message_text(
            msg_no_tariffs(user_id), chat_id, mes_id,
            reply_markup=kb_user_tariff_back(user_id)
        )
    else:
        tariff = tariffs[page]
        tariff_id = tariff.id or 0

        lang = get_lang(user_id)

        if lang == 'en':
            image = tariff.img_en or tariff.img
        else:
            image = tariff.img

        text = msg_user_tariff(user_id, tariff)
        keyboard = kb_tariff_list(
            user_id, tariff_id, count, tariff_type, page, is_rus)

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
            delete_message(bot, chat_id, mes_id)
            send()


def send_calculation(
    bot: TeleBot,
    message: Message,
    user_id: int,
    calc: Calculation,
    is_first=False,
    is_try=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    is_access = pay_guard.valid_use_calc(user_id, bot)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calc_output = db.get_user_calc_output(user_db_id)

    kb = kb_main(user_id, is_access, calc)
    if is_try:
        kb = kb_first_calc_info(user_id)

    if calc_output == 'text' or is_try:
        text = msg_calculation(user_id, calc, is_try)

        if is_first:
            bot.send_message(chat_id, text, reply_markup=kb)
        else:
            edit_message(bot, message, 'text', text, kb)
    else:
        file_path, caption = hti.create_calculation_image(
            user_id, calc
        )

        with open(file_path, 'rb') as photo:
            if not is_first:
                bot.delete_message(chat_id, mes_id)
            bot.send_photo(
                chat_id, photo, caption=caption,
                reply_markup=kb,
            )
        os.remove(file_path)


def send_freeze(
    bot: TeleBot,
    message: Message,
    user_id: int,
    market: MARKETS_TYPE,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    day_risk = calcService.check_day_risk(user_id, market)
    if day_risk:
        bot.set_state(user_id, StatsState.freeze, chat_id)
        set_state_data(bot, user_id, chat_id, {'market': market})

        text = msg_freeze_calc(user_id, day_risk)
        kb = kb_freeze_calc(user_id)

        if is_first:
            bot.send_message(
                chat_id, text,
                reply_markup=kb,
            )
        else:
            edit_message(bot, message, 'text', text, kb)
