from telebot import TeleBot
from telebot.types import Message

from initialize import currencyService
from db import db, BASE_VALUE_TYPE
from common.utils import digit_accept, is_digit, set_state_data, text_accept

from CALCULATE.callbacks import kb_base_cancel, kb_splitting, kb_trading_style, send_settings
from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_currency_error, msg_digit_error, msg_enter_day_risk, msg_enter_deposit,
    msg_enter_risk_percent, msg_enter_round_count, msg_enter_splitting, msg_enter_trading_style,
    msg_success_base_set, msg_success_edit
)


def handle_new_value(type: BASE_VALUE_TYPE):
    if type == 'base_currency':
        return

    def r_func(message: Message, bot: TeleBot):
        user_id = message.from_user.id
        user_db_id = db.get_user_id_by_tg_id(user_id)

        chat_id = message.chat.id

        is_percent = False
        if message.text is not None and message.text.endswith('%'):
            is_percent = True
            message.text = message.text.replace('%', '')

        value = digit_accept(message)
        if value is None:
            bot.send_message(chat_id, msg_digit_error(user_id),
                             reply_markup=kb_base_cancel(user_id))
            return

        # if type == 'base_risk' and (value <= 0 or value >= 100):
        #     bot.send_message(
        #         chat_id,
        #         msg_percent_error(user_id),
        #         reply_markup=kb_base_cancel(user_id)
        #     )
        #     return

        db.set_user_base(user_db_id, type, value)
        if type == 'base_risk':
            db.set_user_risk_is_percent(user_db_id, is_percent)

        with bot.retrieve_data(user_id, chat_id) as data:
            action = data.get('action')

        if action == 'welcome':
            if type == 'base_deposit':
                bot.set_state(user_id, SettingsState.risk_percent, chat_id)
                bot.send_message(chat_id, msg_enter_risk_percent(user_id))
            else:
                bot.set_state(user_id, SettingsState.trading_style, chat_id)
                bot.send_message(
                    chat_id, msg_enter_trading_style(user_id),
                    reply_markup=kb_trading_style(user_id, 'welcome')
                )
        else:
            bot.delete_state(user_id, chat_id)
            bot.send_message(chat_id, msg_success_edit(user_id))
            send_settings(bot, message, user_id, True)

    return r_func


def handle_new_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_base_cancel(user_id)
        )
        return

    check = currencyService.getPrice('USD', value)
    if not check:
        bot.send_message(
            chat_id, 'Валюта не найдена\n' + msg_currency_error(user_id),
            reply_markup=kb_base_cancel(user_id))
        return

    db.set_user_currency(user_db_id, value.upper())

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    if action == 'welcome':
        bot.set_state(user_id, SettingsState.deposit, chat_id)
        bot.send_message(chat_id, msg_enter_deposit(user_id))
    else:
        bot.send_message(chat_id, msg_success_edit(user_id))
        send_settings(bot, message, user_id, True)


def handle_splitting(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        current_tp: list[int] = data.get('take_profit', [])
        current_split: list[float] = data.get('split', [])

    enter_mes = msg_enter_splitting(user_id, current_tp, current_split)

    message.text = message.text.replace('%', '') if (
        message.text is not None) else ''

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id,
            '<i>Введите процент в виде числа</i>\n' + enter_mes
        )
        return

    if sum(current_split) + value > 100:
        bot.send_message(
            chat_id,
            '<i>Суммарный процент превысил 100</i>\n' + enter_mes
        )
        return

    current_split.append(value)
    bot.send_message(
        chat_id, msg_enter_splitting(user_id, current_tp, current_split),
        reply_markup=kb_splitting(user_id, current_tp, current_split)
    )
    set_state_data(bot, user_id, chat_id, {'split': current_split})
    bot.set_state(user_id, SettingsState.summury_profit, chat_id)


def handle_day_risk(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)

    enter_mes = msg_enter_day_risk(user_id)
    keyboard = kb_base_cancel(user_id)

    if value is None:
        bot.send_message(
            chat_id,
            'Введите значение текстом\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    is_percent = value.endswith('%')
    value = value.replace('%', '')

    if not is_digit(value):
        bot.send_message(
            chat_id,
            'Введите число\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    value = float(value)

    db.set_user_day_risk(user_db_id, value, is_percent)
    bot.send_message(chat_id, msg_success_edit(user_id))
    send_settings(bot, message, user_id, True)


def handle_round_count(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = digit_accept(message, int)

    enter_mes = msg_enter_round_count(user_id)
    keyboard = kb_base_cancel(user_id)

    if value is None:
        bot.send_message(
            chat_id,
            'Введите число\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    if value < 0 or value > 5:
        bot.send_message(
            chat_id,
            'Введите число от 0 до 5\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    db.set_user_round_count(user_db_id, value)
    bot.send_message(chat_id, msg_success_edit(user_id))
    send_settings(bot, message, user_id, True)


def handle_trading_style(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)

    if value is None:
        bot.send_message(
            chat_id,
            'Введите стиль текстом\n' + msg_enter_trading_style(user_id),
            reply_markup=kb_base_cancel(user_id)
        )
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    db.set_user_trading_style(user_db_id, value.lower())
    bot.delete_state(user_id, chat_id)

    if action == 'welcome':
        bot.send_message(chat_id, msg_success_base_set(user_id))
    else:
        bot.send_message(chat_id, msg_success_edit(user_id))

    send_settings(bot, message, user_id, True)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_value('base_deposit'),
            state=SettingsState.deposit)
    reg_mes(handle_new_value('base_risk'),
            state=SettingsState.risk_percent)
    reg_mes(handle_day_risk,
            state=SettingsState.day_risk)
    reg_mes(handle_round_count,
            state=SettingsState.round_count)
    reg_mes(handle_trading_style,
            state=SettingsState.trading_style)

    reg_mes(handle_new_currency, state=SettingsState.currency)
    reg_mes(handle_splitting, state=SettingsState.splitting)
