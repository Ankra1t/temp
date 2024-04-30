from telebot import TeleBot
from telebot.types import Message

from Classes import pay_guard
from db import db
from common.utils import set_state_data
from models import MARKETS_TYPE, ForexInfo

from .pages import send_main
from .calculate.keyboards import kb_calc_cancel, kb_pair, kb_price, kb_tool
from .settings.keyboards import kb_change_currency, kb_trading_style

from CALCULATE.common.messages import (
    msg_calculate, msg_enter_currency, msg_enter_deposit,
    msg_enter_open_price, msg_enter_pair, msg_enter_risk_percent,
    msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style
)
from CALCULATE.states import CalculateState, ForexCalcState


def choose_calculate_step(
    bot: TeleBot,
    user_id: int,
    chat_id: int,
    mes_id: int,
    is_edit=False,
    last_value: str | None = None,
):
    with bot.retrieve_data(user_id, chat_id) as data:
        if last_value is not None:
            if data.get('last_values') is None:
                data['last_values'] = [last_value]
            else:
                data['last_values'].append(last_value)

        calc_type: MARKETS_TYPE = data.get('calc_type')
        forex: ForexInfo | None = data.get('forex')
        open_price = data.get('open_price')
        trading_style = data.get('trading_style')
        tool = data.get('tool')
        deposit = data.get('deposit')
        currency = data.get('currency')
        risk = data.get('risk')
        updated_risk = data.get('updated_risk')

    user_db_id = db.get_user_id_by_tg_id(user_id)

    text = msg_calculate(bot, user_id, chat_id)
    keyboard = kb_calc_cancel(user_id)

    if calc_type == 'forex' and forex is None:
        text += msg_enter_pair(user_id)
        state = ForexCalcState.pair
        keyboard = kb_pair(user_id)

    elif calc_type != 'forex' and tool is None:
        text += msg_enter_tool(user_id)
        state = CalculateState.tool

        last_tools = db.get_last_tools(user_db_id, calc_type)
        keyboard = kb_tool(user_id, last_tools)

    elif trading_style is None:
        text += msg_enter_trading_style(user_id)
        state = CalculateState.trading_style
        keyboard = kb_trading_style(user_id, 'calc')

    elif currency is None:
        text += msg_enter_currency(user_id)
        state = CalculateState.currency
        keyboard = kb_change_currency(user_id, 'calc')

    elif deposit is None:
        text += msg_enter_deposit(user_id)
        state = CalculateState.deposit

    elif risk is None:
        text += msg_enter_risk_percent(user_id)
        state = CalculateState.risk_percent

    elif open_price is None:
        text += msg_enter_open_price(user_id)
        state = CalculateState.open_price

        op_value = None
        if calc_type == 'forex' and forex is not None:
            op_value = round(forex.price, 5)

        keyboard = kb_price(user_id, updated_risk is None, op_value)
    else:
        text += msg_enter_stop_loss(user_id)
        state = CalculateState.stop_loss

    bot.set_state(user_id, state, chat_id)

    new_mes_id = mes_id
    if is_edit:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard,
        )
    else:
        new_mes = bot.send_message(
            user_id, text,
            reply_markup=keyboard
        )
        new_mes_id = new_mes.id

    set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes_id})


def choose_first_calculate_step(
    bot: TeleBot, user_id: int, message: Message,
    type: MARKETS_TYPE,
    is_edit=False,
    is_continue=False
):
    chat_id = message.chat.id
    mes_id = message.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    unfinished_calc = db.get_unfinished_calc_by_user(user_db_id)
    db.delete_unfinished_calc_by_user(user_db_id)

    style = deposit = risk = currency = None
    if u_base is not None:
        style = u_base.trading_style
        deposit = u_base.deposit
        currency = u_base.currency
        risk = u_base.risk

    prev_values = {}
    if unfinished_calc is not None and is_continue:
        prev_values['open_price'] = unfinished_calc.open_price
        prev_values['tool'] = unfinished_calc.tool
        prev_values['forex'] = unfinished_calc.forex
        prev_values['last_values'] = unfinished_calc.last_values

        style = unfinished_calc.trading_style or style
        deposit = unfinished_calc.deposit or deposit
        currency = unfinished_calc.currency or currency

        if (
            unfinished_calc.risk_value is not None and
            (risk is None or
             (unfinished_calc.risk_value == risk[0] and unfinished_calc.is_risk_percent == risk[1]))
        ):
            prev_values['updated_risk'] = unfinished_calc.update_risk_rate
            risk = risk or [unfinished_calc.risk_value, unfinished_calc.is_risk_percent]

    # Проверяем подписку
    if not pay_guard.valid_use_calc(user_id):
        send_main(message, bot, user_id, True)
        return

    if type == 'forex':
        bot.set_state(user_id, ForexCalcState.pair, chat_id)
    else:
        bot.set_state(user_id, CalculateState.tool, chat_id)

    set_state_data(
        bot, user_id, chat_id, {
            'calc_type': type,

            'trading_style': style,
            'deposit': deposit,
            'currency': currency,
            'risk': risk,
        } | prev_values
    )
    choose_calculate_step(bot, user_id, chat_id, mes_id, is_edit)
