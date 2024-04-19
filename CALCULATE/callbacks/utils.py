from telebot import TeleBot
from telebot.types import Message

from Classes import pay_guard
from db import db
from common.utils import set_state_data
from models import MARKETS_TYPE, ForexInfo

from .pages import send_main
from .main.keyboards import kb_main_cancel
from .calculate.keyboards import kb_open_price, kb_pair, kb_tool
from .settings.keyboards import kb_change_currency, kb_trading_style

from CALCULATE.common.messages import (
    msg_calculate, msg_enter_currency, msg_enter_deposit,
    msg_enter_open_price, msg_enter_pair, msg_enter_risk_percent, msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style
)
from CALCULATE.states import CalculateState, ForexCalcState


def choose_calculate_step(bot: TeleBot, user_id: int, chat_id: int, mes_id: int, is_edit=False):
    with bot.retrieve_data(user_id, chat_id) as data:
        forex: ForexInfo | None = data.get('forex')
        open_price = data.get('open_price')
        calc_type: MARKETS_TYPE = data.get('calc_type')
        trading_style = data.get('trading_style')
        tool = data.get('tool')

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    if u_base is None:
        return

    text = msg_calculate(bot, user_id, chat_id)
    keyboard = kb_main_cancel(user_id)

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
    elif u_base.currency is None:
        text += msg_enter_currency(user_id)
        state = CalculateState.currency
        keyboard = kb_change_currency(user_id, 'calc')
    elif u_base.deposit is None:
        text += msg_enter_deposit(user_id)
        state = CalculateState.deposit
    elif u_base.risk is None:
        text += msg_enter_risk_percent(user_id)
        state = CalculateState.risk_percent
    elif open_price is None:
        text += msg_enter_open_price(user_id)
        state = CalculateState.open_price

        if calc_type == 'forex' and forex is not None:
            keyboard = kb_open_price(user_id, round(forex.price, 5))
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
    is_edit=False
):
    chat_id = message.chat.id
    mes_id = message.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    style = None
    if u_base is not None:
        style = u_base.trading_style

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
            'trading_style': style
        })
    choose_calculate_step(bot, user_id, chat_id, mes_id, is_edit)
