from typing import Literal
from telebot import TeleBot
from telebot.types import Message

from db_new import db_new
from initialize import pay_guard
from common.utils import set_state_data
from .main.keyboards import kb_cancel, kb_forex_val
from .pages import send_main

from CALCULATE.common.messages import (
    msg_calculate, msg_enter_currency, msg_enter_deposit, msg_enter_future,
    msg_enter_open_price, msg_enter_pair, msg_enter_risk_percent
)
from CALCULATE.states import CalculateState, FutureCalcState, ForexCalcState


def choose_calculate_step(bot: TeleBot, user_id: int, chat_id: int, mes_id: int, is_edit=False):
    with bot.retrieve_data(user_id, chat_id) as data:
        calc_type = data.get('calc_type')
        ticker = data.get('ticker')
        pair = data.get('pair')
        val_dep = data.get('val_dep')

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    res = db_new.get_user_base(user_db_id)

    deposit, risk_percent = res.get('base_deposit'), res.get('base_risk_percent')

    text = msg_calculate(bot, user_id, chat_id)
    keyboard = kb_cancel(user_id)

    if calc_type == 'forex' and pair is None:
        text += msg_enter_pair(user_id)
        state = ForexCalcState.pair
    elif calc_type == 'forex' and val_dep is None:
        text += msg_enter_currency(user_id)
        state = ForexCalcState.val_dep
        keyboard = kb_forex_val()
    elif calc_type == 'future' and ticker is None:
        text += msg_enter_future(user_id)
        state = FutureCalcState.ticker
    elif deposit is None:
        text += msg_enter_deposit(user_id)
        state = CalculateState.deposit
    elif risk_percent is None:
        text += msg_enter_risk_percent(user_id)
        state = CalculateState.risk_percent
    else:
        text += msg_enter_open_price(user_id)
        state = CalculateState.open_price

    bot.set_state(user_id, state, chat_id)
    if is_edit:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            user_id, text,
            reply_markup=keyboard)


def choose_first_calculate_step(bot: TeleBot, user_id: int, message: Message,
                                type: Literal['crypto', 'future', 'paper', 'forex'],
                                is_edit=False):
    chat_id = message.chat.id
    mes_id = message.id

    # Проверяем подписку
    if not pay_guard.valid_use_calc(user_id):
        send_main(message, bot, user_id, True)
        return

    if type == 'forex':
        bot.set_state(user_id, ForexCalcState.pair, chat_id)
    elif type == 'future':
        bot.set_state(user_id, FutureCalcState.ticker, chat_id)
    else:
        bot.set_state(user_id, CalculateState.deposit, chat_id)

    set_state_data(bot, user_id, chat_id, {'calc_type': type})
    choose_calculate_step(bot, user_id, chat_id, mes_id, is_edit)
