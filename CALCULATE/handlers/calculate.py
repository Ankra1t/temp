from telebot import TeleBot
from telebot.types import Message

from db import db
from db_new import db_new
from common.utils import digit_accept, get_calculation, set_state_data, text_accept

from CALCULATE.callbacks import kb_cancel, choose_calculate_step, send_main
from CALCULATE.states import CalculateState, ForexCalcState, FutureCalcState
from CALCULATE.common.messages import (
    msg_calculate, msg_calculate_forex_result, msg_calculate_result,
    msg_digit_error, msg_enter_stop_loss, msg_paire_error,
    msg_paire_not_found, msg_percent_error,
    msg_sl_op_equal_error, msg_ticker_error, msg_ticker_not_found
)


def handle_future_ticker(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    ticker = text_accept(message)
    if ticker is None:
        bot.send_message(chat_id, msg_ticker_error(user_id))
        return

    if not db.check_future(ticker):
        bot.send_message(
            chat_id,
            msg_ticker_not_found(user_id, ticker),
            reply_markup=kb_cancel(user_id))
        return

    set_state_data(bot, user_id, chat_id, {'ticker': ticker})
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_forex_paire(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    paire = text_accept(message)
    if paire is None:
        bot.send_message(chat_id, msg_paire_error(user_id))
        return

    paire = paire.upper().replace(' ', '/')
    price = db.get_price_forex(paire)
    if price is None:
        bot.send_message(
            chat_id, msg_paire_not_found(user_id, paire),
            reply_markup=kb_cancel(user_id))
        return

    # ЕСЛИ ПАРА xxx/USD
    if '/USD' in paire:
        type_forex = 'xxx/USD'
    # Если пара USD/xxx
    elif 'USD/' in paire:
        type_forex = 'USD/xxx'
    # Если кросc
    else:
        help_paire = db.get_help_paire_forex(paire)

        if help_paire is None:
            print(f'ERROR: no help_paire of {paire}')
            return
        if 'USD' not in help_paire:
            print('ERROR: help_paire doesn\'t contain USD')
            return

        price = db.get_price_forex(help_paire)
        if price is None:
            print(f'ERROR: paire {help_paire} doesn\'t contain price')
            return

        # ЕСЛИ ВСПОМОГ. xxx/USD
        if '/USD' in help_paire:
            type_forex = 'CROSSxxx/USD'
        # ЕСЛИ ВСПОМОГ. USD/xxx
        else:
            type_forex = 'CROSSUSD/xxx'

    set_state_data(bot, user_id, chat_id, {
        'forex_type': type_forex,
        'price': price,
        'paire': paire,
    })
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_deposit(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_cancel(user_id))
        return

    db_new.set_user_base(user_id, 'base_deposit', value)

    set_state_data(bot, user_id, chat_id, {'deposit': value})
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_risk_percent(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_cancel(user_id))
        return
    if value <= 0 or value >= 100:
        bot.send_message(
            chat_id,
            msg_percent_error(user_id),
            reply_markup=kb_cancel(user_id))
        return

    db_new.set_user_base(user_db_id, 'base_risk_percent', value)

    set_state_data(bot, user_id, chat_id, {'risk_percent': value})
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_open_price(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, 'Введите число:',
                         reply_markup=kb_cancel(user_id))
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
        reply_markup=kb_cancel(user_id)
    )


def handle_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_cancel(user_id))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        calc_type = data.get('calc_type')
        deposit = data.get('deposit')
        risk_percent = data.get('risk_percent')
        open_price = data.get('open_price')
        ticker = data.get('ticker')

    if open_price == stop_loss:
        bot.send_message(chat_id, msg_sl_op_equal_error(user_id))

    count_bet, value_bet, credit, risk_value, take_profit, profit = get_calculation(
        user_id, deposit, risk_percent, open_price,
        stop_loss, ticker
    )

    mes = msg_calculate_result(
        user_id, deposit, risk_percent, open_price,
        stop_loss, count_bet, value_bet, credit,
        risk_value, take_profit, profit
    )

    db_new.minus_calculator_uses_count(user_db_id)
    bot.send_message(chat_id, mes)
    bot.delete_state(user_id, chat_id)
    send_main(message, bot, user_id, True)


def handle_forex_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        bot.send_message(chat_id, 'Введите число:',
                         reply_markup=kb_cancel(user_id))
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        deposit = data.get('deposit')
        risk_percent = data.get('risk_percent')
        open_price = data.get('open_price')
        forex_type = data.get('forex_type')
        price = data.get('price')
        val_dep = data.get('val_dep')
        paire = data.get('paire')

    diff = open_price - stop_loss
    take_profit_2 = open_price + diff * 2
    take_profit_3 = open_price + diff * 3
    take_profit_4 = open_price + diff * 4

    pips = float(abs(diff) * 10000)

    if val_dep == 'RUB':
        price_usd_rub = db.get_forex_rub_price()[0]
        deposit /= price_usd_rub
    risk = risk_percent / 100

    print_dep = deposit
    risk_value = deposit * risk

    lot = 0
    if forex_type == 'xxx/USD':
        lot = (deposit * risk) / pips
        lot /= 10
    if forex_type == 'USD/xxx':
        lot = (deposit * risk * stop_loss) / pips
        lot /= 10
    if forex_type == 'CROSSxxx/USD':
        lot = (deposit * risk) / (pips * price)
        lot /= 10
    if forex_type == 'CROSSUSD/xxx':
        lot = (deposit * risk * price) / pips
        lot /= 10
    if 'JPY' in paire:
        pips /= 100

# ======================= // ANCHOR УБРАТЬ КОЛИЧЕСТВО ПУНКТОВ
    message_res = msg_calculate_forex_result(
        user_id, print_dep, val_dep, risk_percent,
        paire, open_price, stop_loss, take_profit_2,
        take_profit_3, take_profit_4, lot, risk_value
    )

    db_new.minus_calculator_uses_count(user_db_id)
    bot.send_message(chat_id, message_res)
    bot.delete_state(user_id, chat_id)
    send_main(message, bot, user_id, True)


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
    reg_mes(handle_open_price, state=CalculateState.open_price)
    reg_mes(handle_stop_loss, state=CalculateState.stop_loss)

    reg_mes(handle_forex_paire, state=ForexCalcState.paire)
    reg_mes(handle_future_ticker, state=FutureCalcState.ticker)
    reg_mes(handle_forex_stop_loss, state=ForexCalcState.stop_loss)
