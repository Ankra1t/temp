import os
from telebot import TeleBot
from telebot.types import Message

from common.calculation import get_msg_of_calc
from initialize import currencyService, pay_guard, hti
from db import db
from models import Calculation, ForexInfo

from common.utils import digit_accept, is_digit, set_state_data, text_accept
from CALCULATE.callbacks import kb_main_cancel, choose_calculate_step, kb_tool, kb_main
from CALCULATE.states import CalculateState, ForexCalcState, FutureCalcState
from CALCULATE.common.messages import (
    msg_currency_error, msg_ticker_not_found, msg_trading_style_error,
    msg_digit_error, msg_enter_trading_style, msg_pair_error,
    msg_pair_not_found, msg_sl_op_equal_error, msg_text_error, msg_ticker_error
)


def handle_tool(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    tool = text_accept(message)
    if tool is None or is_digit(tool):
        bot.send_message(
            chat_id, msg_text_error(user_id),
            reply_markup=kb_tool(user_id, [])
        )
        return

    tool = tool.lower().replace('/', '')
    if tool.endswith('usdt'):
        tool = tool.replace('usdt', '')

    tool = tool.strip().upper() + '/USDT'

    set_state_data(bot, user_id, chat_id, {'tool': tool})
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_future_ticker(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    ticker = text_accept(message)
    if ticker is None:
        bot.send_message(chat_id, msg_ticker_error(user_id))
        return

    if db.get_future(ticker) is None:
        bot.send_message(
            chat_id,
            msg_ticker_not_found(user_id, ticker),
            reply_markup=kb_main_cancel(user_id)
        )
        return

    set_state_data(bot, user_id, chat_id, {'ticker': ticker})
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_forex_pair(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    pair = text_accept(message)
    if pair is None or is_digit(pair):
        bot.send_message(chat_id, msg_pair_error(user_id))
        return

    pair = pair.upper().replace(' ', '/')

    pair_arr = pair.split('/')
    if len(pair_arr) != 2 or pair_arr[0] == pair_arr[1]:
        bot.send_message(chat_id, msg_pair_error(user_id))
        return

    user_db_id = db.get_user_id_by_tg_id(user_id)
    user_settings = db.get_calc_user_settings(user_db_id)
    user_currency = getattr(user_settings, 'currency') or 'USD'

    pairs = [pair]
    if user_currency not in pair:
        pairs.append(f'{user_currency}/{pair_arr[1]}')
        pairs.append(f'{pair_arr[0]}/{user_currency}')

    prices = currencyService.getPairsPrice(pairs)

    if prices == False:
        bot.send_message(
            chat_id, msg_pair_not_found(user_id, pair),
            reply_markup=kb_main_cancel(user_id))
        return

    forex = ForexInfo(
        pair=(pair_arr[0], pair_arr[1]),
        price=prices.get(pair, 1),
        cross_prices=prices
    )

    set_state_data(bot, user_id, chat_id, {
        'forex': forex,
    })
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_main_cancel(user_id))
        return

    check = currencyService.getPrice('USD', value)
    if not check:
        bot.send_message(
            chat_id, msg_currency_error(user_id, 'not_found'),
            reply_markup=kb_main_cancel(user_id))
        return

    db.set_user_currency(user_db_id, value.upper())

    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_deposit(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_main_cancel(user_id))
        return

    db.set_user_base(user_db_id, 'base_deposit', value)

    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_risk_percent(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    is_percent = False
    if message.text is not None and message.text.endswith('%'):
        is_percent = True
        message.text = message.text.replace('%', '')

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_main_cancel(user_id)
        )
        return

    # if value <= 0 or value >= 100:
    #     bot.send_message(
    #         chat_id,
    #         msg_percent_error(user_id),
    #         reply_markup=kb_main_cancel(user_id)
    #     )
    #     return

    db.set_user_base(user_db_id, 'base_risk', value)
    db.set_user_risk_is_percent(user_db_id, is_percent)

    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_trading_style(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = text_accept(message)

    msg_error = f'{msg_trading_style_error(user_id)}\n{msg_enter_trading_style(user_id)}'

    if value is None or is_digit(value):
        bot.send_message(
            chat_id, msg_error,
            reply_markup=kb_main_cancel(user_id)
        )
        return

    value = value.lower()

    set_state_data(bot, user_id, chat_id, {'trading_style': value})
    db.set_user_trading_style(user_db_id, value)
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_open_price(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_main_cancel(user_id)
        )
        return

    set_state_data(bot, user_id, chat_id, {'open_price': value})
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_main_cancel(user_id)
        )
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        open_price = data.get('open_price', 0)
        forex = data.get('forex')
        trading_style = data.get('trading_style')
        tool = data.get('tool')

    if open_price == stop_loss:
        bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
        return

    u_base = db.get_calc_user_settings(user_db_id)
    if u_base is None:
        return

    deposit = u_base.deposit or 1.
    risk_value = u_base.risk[0] if (u_base.risk is not None) else 1.
    if u_base.risk is not None and u_base.risk[1]:
        risk_value *= deposit * 0.01

    calc_info = Calculation(
        user_id=user_db_id,
        deposit=deposit,
        risk_value=risk_value,
        open_price=open_price,
        stop_loss=stop_loss,
        round_count=u_base.round_count,
        currency=u_base.currency or 'USD',
        market=u_base.market,
        tp_ratio=u_base.tp_ratio,
        split_values=u_base.split_values,
        trading_style=trading_style or None,
        tool=tool or None,
        forex_info=forex
    )

    new_id = db.add_calculation(calc_info)
    is_valid = pay_guard.valid_use_calc(user_id)

    file_path = hti.create_calculation_image(user_id, calc_info)
    mes = get_msg_of_calc(user_id, calc_info)

    with open(file_path, 'rb') as photo:
        bot.send_photo(
            chat_id, photo, caption=mes,
            reply_markup=kb_main(user_id, is_valid, True, new_id),
        )
    os.remove(file_path)

    db.minus_calculator_uses_count(user_db_id)
    bot.delete_state(user_id, chat_id)


# ? Выравнивание результатов
def user_cal_def(op, sl, tp):
    res = 1
    op_str = str(op)
    op_str = len(op_str) - op_str.index('.') - 1
    sl = str(sl)
    sl = len(sl) - sl.index('.') - 1
    tp = str(tp)
    tp = len(tp) - tp.index('.') - 1
    mx = op_str
    if sl > mx:
        mx = sl
    if tp > mx:
        mx = tp
    for _ in range(0, mx):
        res *= 10
    return res


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_deposit, state=CalculateState.deposit)
    reg_mes(handle_risk_percent, state=CalculateState.risk_percent)
    reg_mes(handle_currency, state=CalculateState.currency)

    reg_mes(handle_tool, state=CalculateState.tool)
    reg_mes(handle_trading_style, state=CalculateState.trading_style)

    reg_mes(handle_open_price, state=CalculateState.open_price)
    reg_mes(handle_stop_loss, state=CalculateState.stop_loss)

    reg_mes(handle_forex_pair, state=ForexCalcState.pair)
    reg_mes(handle_future_ticker, state=FutureCalcState.ticker)
