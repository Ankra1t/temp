from telebot import TeleBot
from telebot.types import Message

from db import db, BASE_VALUE_TYPE
from common.vars import API_URL
from common.utils import digit_accept, text_accept
from CALCULATE.callbacks import kb_base_cancel, send_main, send_settings
from CALCULATE.states import SettingsState
from CALCULATE.common.messages import msg_currency_error, msg_digit_error, msg_enter_currency, msg_enter_risk_percent, msg_percent_error, msg_success_base_set, msg_success_edit

from AuthRoles import change_password

def handle_new_value(type: BASE_VALUE_TYPE):
    if type == 'base_currency':
        return

    def r_func(message: Message, bot: TeleBot):
        user_id = message.from_user.id
        chat_id = message.chat.id

        value = digit_accept(message)
        if value is None:
            bot.send_message(chat_id, msg_digit_error(user_id),
                             reply_markup=kb_base_cancel(user_id))
            return
        if type == 'base_risk_percent' and (value <= 0 or value >= 100):
            bot.send_message(
                chat_id,
                msg_percent_error(user_id),
                reply_markup=kb_base_cancel(user_id))
            return

        db.set_user_base(user_id, type, value)

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
    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_base_cancel(user_id))
        return

    db.set_user_currency(user_id, value.upper())

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    if action == 'welcome':
        bot.send_message(chat_id, msg_success_base_set(user_id))
        send_main(message, bot, user_id, True)
    else:
        bot.send_message(chat_id, msg_success_edit(user_id))
        send_settings(bot, message, user_id, True)

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_value('base_deposit'),
            state=SettingsState.deposit)
    reg_mes(handle_new_value('base_risk_percent'),
            state=SettingsState.risk_percent)

    reg_mes(handle_new_currency, state=SettingsState.currency)
