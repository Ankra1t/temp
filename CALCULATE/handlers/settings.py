from telebot import TeleBot
from telebot.types import Message
from CALCULATE.callbacks.settings.keyboards import kb_splitting

from db_new import db_new, BASE_VALUE_TYPE
from common.utils import digit_accept, is_digit, set_state_data, text_accept
from CALCULATE.callbacks import kb_base_cancel, send_main, send_settings, kb_split_settings
from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_currency_error, msg_digit_error, msg_enter_currency,
    msg_enter_risk_percent, msg_enter_split, msg_enter_splitting, msg_percent_error, msg_split_settings,
    msg_success_base_set, msg_success_edit
)


def handle_new_value(type: BASE_VALUE_TYPE):
    if type == 'base_currency':
        return

    def r_func(message: Message, bot: TeleBot):
        user_id = message.from_user.id
        user_db_id = db_new.get_user_id_by_tg_id(user_id)

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

        # if type == 'base_risk_percent' and (value <= 0 or value >= 100):
        #     bot.send_message(
        #         chat_id,
        #         msg_percent_error(user_id),
        #         reply_markup=kb_base_cancel(user_id)
        #     )
        #     return

        db_new.set_user_base(user_db_id, type, value)
        if type == 'base_risk_percent':
            db_new.set_user_risk_is_percent(user_db_id, is_percent)

        with bot.retrieve_data(user_id, chat_id) as data:
            action = data.get('action')

        if action == 'welcome':
            if type == 'base_deposit':
                state = SettingsState.risk_percent
                text = msg_enter_risk_percent(user_id)
            else:
                state = SettingsState.currency
                text = msg_enter_currency(user_id)

            bot.set_state(user_id, state, chat_id)
            bot.send_message(chat_id, text)
        else:
            bot.delete_state(user_id, chat_id)
            bot.send_message(chat_id, msg_success_edit(user_id))
            send_settings(bot, message, user_id, True)

    return r_func


def handle_new_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_base_cancel(user_id))
        return

    db_new.set_user_currency(user_db_id, value.upper())

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    if action == 'welcome':
        bot.send_message(chat_id, msg_success_base_set(user_id))
        send_main(message, bot, user_id, True)
    else:
        bot.send_message(chat_id, msg_success_edit(user_id))
        send_settings(bot, message, user_id, True)

    bot.delete_state(user_id, chat_id)


def handle_split_values(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    tp_ratio = db_new.get_calculator_tp_ratio(user_db_id) or '345'

    chat_id = message.chat.id

    error_mes = 'Ошибка!\n' + msg_enter_split(user_id)

    value = text_accept(message)
    if value is None:
        bot.send_message(chat_id, error_mes)
        return

    value = value.replace('%', '')
    split_values = value.split(' ')

    if len(split_values) != len(tp_ratio):
        bot.send_message(chat_id, error_mes)
        return

    values: list[float] = []

    for el in split_values:
        if not is_digit(el):
            bot.send_message(chat_id, error_mes)
            return

        values.append(float(el))

    if sum(values) != 100:
        bot.send_message(chat_id, error_mes)
        return

    db_new.set_user_is_splitting(user_db_id, True)

    bot.delete_state(user_id, chat_id)
    db_new.set_user_split_values(user_db_id, values)
    bot.send_message(
        chat_id, msg_split_settings(user_id),
        reply_markup=kb_split_settings(user_id)
    )


def handle_splitting(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        current_tp: list[int] = data.get('take_profit', [])
        current_split: list[float] = data.get('split', [])

    enter_mes = msg_enter_splitting(user_id, current_tp, current_split)

    message.text = message.text.replace(
        '%', '') if message.text is not None else ''

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
            '<i>Сумма процентов превысила 100</i>\n' + enter_mes
        )
        return

    current_split.append(value)
    bot.send_message(
        chat_id, msg_enter_splitting(user_id, current_tp, current_split),
        reply_markup=kb_splitting(user_id, current_tp, current_split)
    )
    set_state_data(bot, user_id, chat_id, {'split': current_split})
    bot.set_state(user_id, SettingsState.summury_profit, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_value('base_deposit'),
            state=SettingsState.deposit)
    reg_mes(handle_new_value('base_risk_percent'),
            state=SettingsState.risk_percent)

    reg_mes(handle_new_currency, state=SettingsState.currency)
    reg_mes(handle_split_values, state=SettingsState.split_values)
    reg_mes(handle_splitting, state=SettingsState.splitting)
