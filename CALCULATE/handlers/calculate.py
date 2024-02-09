from telebot import TeleBot
from telebot.types import Message

from db_new import db_new
from common.utils import digit_accept, get_calculation, set_state_data, text_accept

from CALCULATE.callbacks import kb_cancel, choose_calculate_step, send_main
from CALCULATE.states import CalculateState, ForexCalcState, FutureCalcState
from CALCULATE.common.messages import (
    msg_calculate, msg_calculate_forex_result, msg_calculate_result,
    msg_digit_error, msg_enter_stop_loss, msg_pair_error,
    msg_pair_not_found, msg_percent_error,
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

    if db_new.get_future(ticker) is None:
        bot.send_message(
            chat_id,
            msg_ticker_not_found(user_id, ticker),
            reply_markup=kb_cancel(user_id)
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

    forex = db_new.get_forex(pair)
    if forex is None:
        bot.send_message(
            chat_id, msg_pair_not_found(user_id, pair),
            reply_markup=kb_cancel(user_id))
        return

    price = forex.price

    if '/USD' in pair:
        type_forex = 'xxx/USD'
    elif 'USD/' in pair:
        type_forex = 'USD/xxx'
    else:
        help_pair = forex.help_pair

        if help_pair is None:
            print(f'ERROR: no help_pair of {pair}')
            return
        if 'USD' not in help_pair:
            print('ERROR: help_pair doesn\'t contain USD')
            return

        forex_help = db_new.get_forex(help_pair)
        if forex_help is None:
            print(f'ERROR: pair {help_pair} doesn\'t contain price')
            return

        price = forex_help.price

        if '/USD' in help_pair:
            type_forex = 'CROSSxxx/USD'
        else:
            type_forex = 'CROSSUSD/xxx'

    set_state_data(bot, user_id, chat_id, {
        'forex_type': type_forex,
        'price': price,
        'pair': pair,
    })
    choose_calculate_step(bot, user_id, chat_id, mes_id)


def handle_deposit(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        bot.send_message(chat_id, msg_digit_error(user_id),
                         reply_markup=kb_cancel(user_id))
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
            reply_markup=kb_cancel(user_id)
        )
        return

    # if value <= 0 or value >= 100:
    #     bot.send_message(
    #         chat_id,
    #         msg_percent_error(user_id),
    #         reply_markup=kb_cancel(user_id)
    #     )
    #     return

    db_new.set_user_base(user_db_id, 'base_risk_percent', value)
    db_new.set_user_risk_is_percent(user_db_id, is_percent)

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
        open_price = data.get('open_price')
        ticker = data.get('ticker')

    if open_price == stop_loss:
        bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
        return

    base_values = db_new.get_user_base(user_db_id)
    risk_is_percent = db_new.get_user_risk_is_percent(user_db_id)

    deposit: float = base_values['base_deposit'] or 1.
    risk_value: float = base_values['base_risk_percent'] or 1.

    if risk_is_percent:
        risk_value *= deposit * 0.01

    count_bet, value_bet, credit, take_profit, profit = get_calculation(
        deposit, risk_value, open_price, stop_loss, ticker
    )

    mes = msg_calculate_result(
        user_id, deposit, open_price,
        stop_loss, count_bet, value_bet, credit,
        risk_value, take_profit, profit
    )

    db_new.minus_calculator_uses_count(user_db_id)
    bot.send_message(chat_id, mes)
    bot.delete_state(user_id, chat_id)
    send_main(message, bot, user_id, True, True)


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
        pair = data.get('pair')

    diff = open_price - stop_loss
    take_profit_2 = open_price + diff * 2
    take_profit_3 = open_price + diff * 3
    take_profit_4 = open_price + diff * 4

    pips = float(abs(diff) * 10000)

    if val_dep == 'RUB':
        usd_rub_forex = db_new.get_forex('USD/RUB')
        price_usd_rub = usd_rub_forex.price if (
            usd_rub_forex is not None) else 1
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
    if 'JPY' in pair:
        pips /= 100

# ======================= // ANCHOR УБРАТЬ КОЛИЧЕСТВО ПУНКТОВ
    message_res = msg_calculate_forex_result(
        user_id, print_dep, val_dep, risk_percent,
        pair, open_price, stop_loss, take_profit_2,
        take_profit_3, take_profit_4, lot, risk_value
    )

    db_new.minus_calculator_uses_count(user_db_id)
    bot.send_message(chat_id, message_res)
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
    reg_mes(handle_open_price, state=CalculateState.open_price)
    reg_mes(handle_stop_loss, state=CalculateState.stop_loss)

    reg_mes(handle_forex_pair, state=ForexCalcState.pair)
    reg_mes(handle_future_ticker, state=FutureCalcState.ticker)
    reg_mes(handle_forex_stop_loss, state=ForexCalcState.stop_loss)
