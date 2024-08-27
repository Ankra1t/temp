from telebot import TeleBot
from telebot.types import Message

from Classes import pay_guard
from data.data import liteDb
from db import db
from common.utils import get_lang, set_state_data
from models import MARKETS_TYPE, ForexInfo
from services import ticker

from .pages import create_and_send_calc, send_main
from .calculate.keyboards import kb_calc_atr, kb_calc_cancel, kb_calc_direct, kb_pair, kb_price, kb_tool
from .settings.keyboards import kb_change_currency, kb_trading_style

from messages.enter import (
    msg_choose_direct, msg_enter_atr, msg_enter_currency, msg_enter_deposit,
    msg_enter_open_price, msg_enter_pair,
    msg_enter_pair_price, msg_enter_risk_percent,
    msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style,
)
from CALCULATE.states import CalculateState, ForexCalcState


names = {
    'ru': {
        'dep': 'Депозит',
        'risk': 'Риск',
        'currency': 'Валюта',
        'pair': 'Пара',
        'tool': 'Инструмент',
        'style': 'Стиль',
        'op': 'Цена входа',
        'sl': 'Стоп-лосс',
        'atr': 'ATR',
    },
    'en': {
        'dep': 'Deposit',
        'risk': 'Risk',
        'currency': 'Currency',
        'pair': 'Pair',
        'tool': 'Tool',
        'style': 'Style',
        'op': 'Open price',
        'sl': 'Stop loss',
        'atr': 'ATR',
    },
    'uz': {
        'dep': 'Depozit',
        'risk': 'Xavf',
        'currency': 'Valyuta',
        'pair': 'Juftlik',
        'tool': 'Asbob',
        'style': 'Uslubi',
        'op': 'Ochiq narx',
        'sl': 'Stop loss',
        'atr': 'ATR',
    },
    'tr': {
        'dep': 'Depozito',
        'risk': 'Risk',
        'currency': 'Para birimi',
        'pair': 'Çift',
        'tool': 'Enstrüman',
        'style': 'Tarzı',
        'op': 'açılış fiyatını',
        'sl': 'Stop loss',
        'atr': 'ATR',
    },
}


def choose_calculate_step(
    bot: TeleBot,
    user_id: int,
    message: Message,
    is_edit=False,
    last_value: str | None = None,
):
    chat_id = message.chat.id
    mes_id = message.id

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
        is_try = data.get('is_try', False)
        stop_type = data.get('stop_type', 'default')
        stop_loss = data.get('stop_loss')

    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)
    is_style_change = liteDb.getStyleChange(user_id) and trading_style is None

    # text = msg_calculate(bot, user_id, chat_id, is_try)
    text = ''
    keyboard = kb_calc_cancel(user_id)

    if currency is None:
        text += msg_enter_currency(lang)
        edit_to = names[lang]['currency']
        state = CalculateState.currency
        keyboard = kb_change_currency(user_id, 'calc')

    elif calc_type == 'forex' and forex is None:
        text += msg_enter_pair(lang)
        edit_to = names[lang]['pair']
        state = ForexCalcState.pair
        keyboard = kb_pair(user_id)

    elif calc_type != 'forex' and tool is None:
        text += msg_enter_tool(lang, calc_type)
        edit_to = names[lang]['tool']
        state = CalculateState.tool

        if is_try:
            last_tools = ['BTC', 'ETH', 'TON']
        else:
            last_tools = db.get_last_tools(user_db_id, calc_type)

        keyboard = kb_tool(user_id, last_tools)

    elif (
        calc_type == 'forex' and
        forex is not None and
        currency not in forex.pair and
        (
            len(forex.cross_prices.keys()) == 0 or
            len(forex.cross_prices.keys()) == 1
        )
    ):
        pair = f'{currency}/{forex.pair[1]}'

        if pair in forex.cross_prices:
            pair = f'{forex.pair[0]}/{currency}'

        text += msg_enter_pair_price(lang, pair)
        edit_to = pair
        state = ForexCalcState.pair_price
        set_state_data(bot, user_id, chat_id, {'current_pair': pair})

    elif is_style_change:
        text += msg_enter_trading_style(lang)
        edit_to = names[lang]['style']
        state = CalculateState.trading_style
        keyboard = kb_trading_style(user_id, 'calc')

    elif deposit is None:
        text += msg_enter_deposit(lang)
        edit_to = names[lang]['dep']
        state = CalculateState.deposit

    elif risk is None:
        text += msg_enter_risk_percent(lang)
        edit_to = names[lang]['risk']
        state = CalculateState.risk_percent

    elif open_price is None:
        text += msg_enter_open_price(lang, is_try)
        edit_to = names[lang]['op']
        state = CalculateState.open_price

        op_value = None
        if calc_type == 'forex' and forex is not None:
            op_value = round(forex.price, 5)

        keyboard = kb_price(user_id, updated_risk is None, op_value)
    elif stop_loss == -1:
        bot.send_message(
            chat_id, msg_choose_direct(lang, user_id),
            reply_markup=kb_calc_direct(user_id)
        )
        return
    else:
        if 'atr' in stop_type:
            text += msg_enter_atr(lang)
            edit_to = names[lang]['atr']
            state = CalculateState.stop_atr

            atr_settings = liteDb.getUserAtrSettings(user_id)
            period, count = atr_settings[1].split('+')

            value = ticker.get_atr(tool, period, int(count)) or None

            if atr_settings[0] and value is not None:
                rate = 1
                if 'atr_percent' in stop_type:
                    _, percent = stop_type.split('+')
                    rate = float(percent) * 0.01

                set_state_data(
                    bot, user_id, chat_id, {
                        'atr': abs(value) * abs(rate)
                    }
                )
                bot.send_message(
                    chat_id, msg_choose_direct(lang, value),
                    reply_markup=kb_calc_direct(user_id)
                )
                return

            keyboard = kb_calc_atr(user_id, value)
        else:
            if stop_loss is None:
                text += msg_enter_stop_loss(lang, is_try)
                edit_to = names[lang]['sl']
                state = CalculateState.stop_loss
            else:
                bot.delete_message(chat_id, mes_id)
                create_and_send_calc(bot, message, user_id, stop_loss)
                return

    bot.set_state(user_id, state, chat_id)

    if is_edit:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard,
        )
        new_mes_id = mes_id
    else:
        new_mes = bot.send_message(
            user_id, text,
            reply_markup=keyboard
        )
        new_mes_id = new_mes.id

    if not is_try:
        set_state_data(
            bot, user_id, chat_id, {
                'del_mes_id': new_mes_id,
                'edit_mes': edit_to
            }
        )


def choose_first_calculate_step(
    bot: TeleBot, user_id: int, message: Message,
    type: MARKETS_TYPE,
    is_edit=False,
    is_continue=False,
    is_try=False,
    is_channel_calc=False
):
    chat_id = message.chat.id
    mes_id = message.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    stop_type = liteDb.getUserStop(user_id)
    unfinished_calc = db.get_unfinished_calc_by_user(user_db_id)
    db.delete_unfinished_calc_by_user(user_db_id)

    is_from_deposit = False
    style = deposit = risk = currency = trading_type = None
    if u_base is not None:
        style = u_base.trading_style
        deposit = u_base.deposit
        currency = u_base.currency
        risk = u_base.risk
        trading_type = u_base.trading_type
        is_from_deposit = u_base.is_from_deposit

    is_style_change = liteDb.getStyleChange(user_id)
    if is_style_change:
        style = None

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
            risk = risk or [unfinished_calc.risk_value,
                            unfinished_calc.is_risk_percent]

    # Проверяем подписку
    if not pay_guard.valid_use_calc(user_id, bot):
        send_main(message, bot, user_id, True)
        return

    bot.delete_state(user_id, chat_id)
    if type == 'forex':
        bot.set_state(user_id, ForexCalcState.pair, chat_id)
    else:
        bot.set_state(user_id, CalculateState.tool, chat_id)

    liteDb.addStartCalcCount(user_id)

    set_state_data(
        bot, user_id, chat_id, {
            'tool': None if not is_try else 'BTC/USDT',
            'open_price': None if not is_try else 62000,
            'stop_loss': (-1 if is_channel_calc else None) if not is_try else 61800,

            'calc_type': type if not is_try else 'crypto',
            'stop_type': (stop_type or '') if not is_try else 'default',

            'trading_style': style,
            'trading_type': trading_type,
            'deposit': deposit if not is_try else 10000,
            'currency': currency if not is_try else 'USDT',
            'risk': risk if not is_try else (1, True),
            'is_try': is_try,
            'is_from_deposit': is_from_deposit,
        } | prev_values
    )
    choose_calculate_step(bot, user_id, message, is_edit)


def send_calc_start(bot: TeleBot, message: Message, user_id: int, is_continue=False, is_try=False, is_edit=False, is_channel_calc=False):
    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)
    market = u_base.market if (u_base is not None) else 'crypto'

    choose_first_calculate_step(
        bot, user_id, message, market, is_edit, is_continue, is_try, is_channel_calc
    )
