from locale import currency
from telebot import TeleBot
from telebot.types import Message

from initialize import currencyService
from db_new import db_new
from models import Calculation

from common.utils import digit_accept, set_state_data, text_accept
from CALCULATE.callbacks import kb_main_cancel, choose_calculate_step, send_main, kb_set_calc_stats
from CALCULATE.states import CalculateState, ForexCalcState, FutureCalcState
from CALCULATE.common.messages import (
    msg_calculate, msg_calculate_forex_result, msg_calculate_result, msg_currency_error,
    msg_digit_error, msg_enter_stop_loss, msg_enter_trading_style, msg_pair_error,
    msg_pair_not_found, msg_sl_op_equal_error, msg_ticker_error, msg_ticker_not_found
)


def handle_future_ticker(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    ticker = text_accept(message)
    if ticker is None:
        bot.send_message(chat_id, msg_ticker_error(user_id))
        return

    if db_new.get_future(ticker) is None:
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
    if pair is None:
        bot.send_message(chat_id, msg_pair_error(user_id))
        return

    pair = pair.upper().replace(' ', '/')

    pair_arr = pair.split('/')
    if len(pair_arr) != 2:
        bot.send_message(chat_id, msg_pair_error(user_id))
        return

    price = currencyService.getPrice(pair_arr[0], pair_arr[1])
    if price == False:
        bot.send_message(
            chat_id, msg_pair_not_found(user_id, pair),
            reply_markup=kb_main_cancel(user_id))
        return

    if '/USD' in pair:
        type_forex = 'xxx/USD'
    elif 'USD/' in pair:
        type_forex = 'USD/xxx'
    else:
        type_forex = 'CROSSUSD/xxx'

    set_state_data(bot, user_id, chat_id, {
        'forex_type': type_forex,
        'price': price,
        'pair': pair,
    })
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_main_cancel(user_id))
        return

    db_new.set_user_currency(user_db_id, value.upper())

    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_deposit(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_main_cancel(user_id))
        return

    db_new.set_user_base(user_db_id, 'base_deposit', value)

    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_risk_percent(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

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

    db_new.set_user_base(user_db_id, 'base_risk', value)
    db_new.set_user_risk_is_percent(user_db_id, is_percent)

    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_trading_style(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = text_accept(message)

    if value is None:
        bot.send_message(
            chat_id,
            'Введите стиль текстом\n' + msg_enter_trading_style(user_id),
            reply_markup=kb_main_cancel(user_id)
        )
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    db_new.set_user_trading_style(user_db_id, value.lower())
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_open_price(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, 'Введите число:',
                         reply_markup=kb_main_cancel(user_id))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        calc_type = data.get('calc_type')
        data['open_price'] = value

    if calc_type is not None and calc_type == 'forex':
        state = ForexCalcState.stop_loss
    else:
        state = CalculateState.stop_loss

    text = msg_calculate(bot, user_id, chat_id) + \
        msg_enter_stop_loss(user_id)

    bot.set_state(user_id, state, chat_id)
    bot.send_message(
        chat_id, text,
        reply_markup=kb_main_cancel(user_id)
    )


def handle_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_main_cancel(user_id))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        open_price = data.get('open_price')
        ticker = data.get('ticker')

    if open_price == stop_loss:
        bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
        return

    u_base = db_new.get_calc_user_settings(user_db_id)
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
        trading_style=u_base.trading_style or ''
    )

    mes = msg_calculate_result(user_id, calc_info)

    new_id = db_new.add_calculation(calc_info)

    db_new.minus_calculator_uses_count(user_db_id)
    bot.send_message(
        chat_id, mes,
        reply_markup=kb_set_calc_stats(user_id, new_id)
    )
    bot.delete_state(user_id, chat_id)
    send_main(message, bot, user_id, True, True)


def handle_forex_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        bot.send_message(chat_id, 'Введите число:',
                         reply_markup=kb_main_cancel(user_id))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        open_price = float(data.get('open_price', 0))
        price = float(data.get('price', 0))
        forex_type = data.get('forex_type', 0)
        pair = data.get('pair')

    u_base = db_new.get_calc_user_settings(user_db_id)
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
        trading_style=u_base.trading_style or ''
    )

    diff = open_price - stop_loss
    take_profit_2 = open_price + diff * 2
    take_profit_3 = open_price + diff * 3
    take_profit_4 = open_price + diff * 4

    pips = abs(diff) * 10000

    if u_base.currency == 'RUB':
        usd_rub_price = currencyService.getPrice('USD', 'RUB') or 1.
        deposit /= usd_rub_price

    lot = 0
    if forex_type == 'xxx/USD':
        lot = (risk_value) / pips
    if forex_type == 'USD/xxx':
        lot = (risk_value * stop_loss) / pips
    if forex_type == 'CROSSxxx/USD':
        lot = (risk_value) / (pips * price)
    if forex_type == 'CROSSUSD/xxx':
        lot = (risk_value * price) / pips

    lot /= 10
    if 'JPY' in pair:
        pips /= 100

    message_res = msg_calculate_forex_result(
        user_id, deposit, u_base.currency or 'USD', 0,
        pair, open_price, stop_loss, take_profit_2,
        take_profit_3, take_profit_4, lot, risk_value
    )

    # db_new.minus_calculator_uses_count(user_db_id)
    # bot.send_message(chat_id, message_res)
    # bot.delete_state(user_id, chat_id)
    # send_main(message, bot, user_id, True, True)

    mes = msg_calculate_result(user_id, calc_info, pair, round(price, 4))

    new_id = db_new.add_calculation(calc_info)
    db_new.minus_calculator_uses_count(user_db_id)

    bot.send_message(
        chat_id, mes,
        # reply_markup=kb_set_calc_stats(user_id, new_id)
    )
    bot.delete_state(user_id, chat_id)
    send_main(message, bot, user_id, True, True)


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

    reg_mes(handle_trading_style, state=CalculateState.trading_style)

    reg_mes(handle_open_price, state=CalculateState.open_price)
    reg_mes(handle_stop_loss, state=CalculateState.stop_loss)

    reg_mes(handle_forex_pair, state=ForexCalcState.pair)
    reg_mes(handle_future_ticker, state=FutureCalcState.ticker)
    reg_mes(handle_forex_stop_loss, state=ForexCalcState.stop_loss)
