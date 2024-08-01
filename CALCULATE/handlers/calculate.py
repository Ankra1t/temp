import re
from telebot import TeleBot
from telebot.types import Message

from MAIN.start import start_with_calc
from config_logger import logger
from Classes import currencyService
from db import db
from models import MARKETS_TYPE, ForexInfo

from common.utils import digit_accept, is_digit, set_state_data, text_accept
from CALCULATE.callbacks import (
    choose_calculate_step, kb_tool,
    send_calculation, kb_change_currency,
    kb_calc_cancel, kb_trading_style,
    kb_calc_direct, create_and_send_calc
)
from CALCULATE.states import CalculateState, ForexCalcState
from CALCULATE.common.messages import (
    msg_choose_direct, msg_currency_error, msg_enter_min_bar, msg_latin_error, msg_trading_style_error,
    msg_digit_error, msg_enter_trading_style, msg_pair_error,
    msg_sl_op_equal_error, msg_text_error,
)
from services import calculation


def handle_tool(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    tool = text_accept(message)
    if tool is None or is_digit(tool):
        new_mes = bot.send_message(
            chat_id, msg_text_error(user_id),
            reply_markup=kb_tool(user_id, [])
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    if not re.match(r'^[a-zA-Z0-9 ]+$', tool):
        new_mes = bot.send_message(
            chat_id, msg_latin_error(user_id),
            reply_markup=kb_tool(user_id, [])
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(f'callback "handle_tool" user_tg_id={user_id} value={tool}')

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')
        calc_type: MARKETS_TYPE = data.get('calc_type', 'crypto')

    tool = tool.upper().replace('/', '').replace(' ', '')

    if calc_type == 'crypto':
        if tool.endswith('USDT'):
            tool = tool.replace('USDT', '')
        tool += '/USDT'

    if stat_id is None:
        set_state_data(bot, user_id, chat_id, {'tool': tool})
        choose_calculate_step(bot, user_id, message, last_value='tool')
    else:
        db.change_calculation_tool(stat_id, tool)

        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)


def handle_forex_pair(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    pair = text_accept(message)
    if pair is None or is_digit(pair):
        new_mes = bot.send_message(chat_id, msg_pair_error(user_id))
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    if not re.match(r'^[a-zA-Z \/]+$', pair):
        new_mes = bot.send_message(
            chat_id, msg_pair_error(user_id),
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_forex_pair" user_tg_id={user_id} value={pair}')

    pair = pair.upper().replace(' ', '/')

    pair_arr = pair.split('/')
    if len(pair_arr) != 2 or pair_arr[0] == pair_arr[1]:
        new_mes = bot.send_message(chat_id, msg_pair_error(user_id))
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    user_db_id = db.get_user_id_by_tg_id(user_id)
    user_settings = db.get_calc_user_settings(user_db_id)
    user_currency = getattr(user_settings, 'currency') or 'USD'

    pairs = [pair]
    if user_currency not in pair:
        pairs.append(f'{user_currency}/{pair_arr[1]}')
        pairs.append(f'{pair_arr[0]}/{user_currency}')

    prices = currencyService.getPairsPrice(pairs)

    # if prices == False and len(pairs) == 3:
    #     new_mes = bot.send_message(
    #         chat_id, msg_pair_not_found(user_id, pair),
    #         reply_markup=kb_pair(user_id)
    #     )
    #     set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
    #     return

    forex = ForexInfo(
        pair=(pair_arr[0], pair_arr[1]),
        price=(prices or {}).get(pair, 1),
        cross_prices=prices or {}
    )

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')

    if stat_id is None:
        set_state_data(bot, user_id, chat_id, {'forex': forex})
        choose_calculate_step(
            bot, user_id, message, last_value='forex'
        )
    else:
        db.change_calculation_forex(stat_id, forex)

        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)


def handle_forex_pair_price(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    pair_price = digit_accept(message)
    if pair_price is None:
        new_mes = bot.send_message(chat_id, msg_pair_error(user_id))
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_forex_pair_price" user_tg_id={user_id} value={pair_price}'
    )

    with bot.retrieve_data(user_id, chat_id) as data:
        forex: ForexInfo = data.get('forex')
        current_pair = data.get('current_pair')

        forex.cross_prices[current_pair] = pair_price
        data['forex'] = forex

    set_state_data(bot, user_id, chat_id, {'forex': forex})
    choose_calculate_step(
        bot, user_id, message, last_value='forex'
    )


def handle_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id

    chat_id = message.chat.id
    mes_id = message.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        new_mes = bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_change_currency(user_id, 'calc')
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_currency" user_tg_id={user_id} value={value}')

    check = currencyService.getPrice('USD', value)
    if not check:
        new_mes = bot.send_message(
            chat_id, msg_currency_error(user_id, 'not_found'),
            reply_markup=kb_change_currency(user_id, 'calc')
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    set_state_data(bot, user_id, chat_id, {'currency': value.upper()})
    choose_calculate_step(bot, user_id, message, last_value='currency')


def handle_deposit(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(f'callback "handle_deposit" user_tg_id={user_id} value={value}')

    set_state_data(bot, user_id, chat_id, {'deposit': value})
    choose_calculate_step(bot, user_id, message, last_value='deposit')


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
            reply_markup=kb_calc_cancel(user_id)
        )
        return

    logger.info(
        f'callback "handle_risk_percent" user_tg_id={user_id} value={value}')

    # if value <= 0 or value >= 100:
    #     bot.send_message(
    #         chat_id,
    #         msg_percent_error(user_id),
    #         reply_markup=kb_calc_cancel(user_id)
    #     )
    #     return

    set_state_data(bot, user_id, chat_id, {'risk': [value, is_percent]})
    choose_calculate_step(bot, user_id, message, last_value='risk')


def handle_trading_style(message: Message, bot: TeleBot):
    user_id = message.from_user.id

    chat_id = message.chat.id
    mes_id = message.id

    value = text_accept(message)

    if value is None or is_digit(value):
        msg_error = f'{msg_trading_style_error(user_id)}\n{msg_enter_trading_style(user_id)}'
        new_mes = bot.send_message(
            chat_id, msg_error,
            reply_markup=kb_trading_style(user_id, 'calc')
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_trading_style" user_tg_id={user_id} value={value}')

    value = value.lower()

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')

    if stat_id is None:
        set_state_data(bot, user_id, chat_id, {'trading_style': value})
        choose_calculate_step(
            bot, user_id, message,
            last_value='trading_style'
        )
    else:
        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        db.change_calculation_style(stat_id, value)
        calc_info.tradingStyle = value

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)


def handle_open_price(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_open_price" user_tg_id={user_id} value={value}')

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')

    if stat_id is None:
        set_state_data(bot, user_id, chat_id, {'open_price': value})
        choose_calculate_step(
            bot, user_id, message, last_value='open_price'
        )
    else:
        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        if calc_info.stopLoss == value:
            new_mes = bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
            set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
            return

        db.change_calculation_open_price(stat_id, value)
        calc_info.openPrice = value

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)


def handle_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action', '')
        stat_id = data.get('stat_id', '')
        open_price = data.get('open_price', '')

    if stop_loss == open_price:
        new_mes = bot.send_message(
            chat_id, msg_sl_op_equal_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_stop_loss" user_tg_id={user_id} value={stop_loss}'
    )

    if action == 'send_calc':
        start_with_calc(bot, message, user_id, stat_id, stop_loss)
    else:
        create_and_send_calc(bot, message, user_id, stop_loss)


def handle_stop_atr(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    stop_atr = digit_accept(message)
    if stop_atr is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_stop_atr" user_tg_id={user_id} value={stop_atr}'
    )

    with bot.retrieve_data(user_id, chat_id) as data:
        stop_type = data.get('stop_type', 'default')
        action = data.get('action', '')

    rate = 1
    if 'atr_percent' in stop_type:
        _, percent = stop_type.split('+')
        rate = float(percent) * 0.01

    new_mes = bot.send_message(
        chat_id, msg_choose_direct(user_id),
        reply_markup=kb_calc_direct(user_id, action == 'send_calc')
    )

    set_state_data(
        bot, user_id, chat_id, {
            'del_mes_id': new_mes.id,
            'atr': abs(stop_atr) * abs(rate)
        }
    )


def handle_max_bar(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    max_bar = digit_accept(message)
    if max_bar is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    new_mes = bot.send_message(
        chat_id, msg_enter_min_bar(user_id),
        reply_markup=kb_calc_cancel(user_id)
    )
    set_state_data(
        bot, user_id, chat_id, {
            'max_bar': max_bar,
            'del_mes_id': new_mes.id
        })
    bot.set_state(user_id, CalculateState.min_bar, chat_id)


def handle_min_bar(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    min_bar = digit_accept(message)
    if min_bar is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        max_bar = data.get('max_bar', 0)
        stop_type = data.get('stop_type', 'default')
        action = data.get('action', '')

    rate = 1
    if 'atr_percent' in stop_type:
        _, percent = stop_type.split('+')
        rate = float(percent) * 0.01

    new_mes = bot.send_message(
        chat_id, msg_choose_direct(user_id),
        reply_markup=kb_calc_direct(user_id, action == 'send_calc')
    )

    set_state_data(
        bot, user_id, chat_id, {
            'del_mes_id': new_mes.id,
            'atr': abs(max_bar - min_bar) * abs(rate)
        }
    )


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
    reg_mes(handle_stop_atr, state=CalculateState.stop_atr)

    reg_mes(handle_forex_pair, state=ForexCalcState.pair)
    reg_mes(handle_forex_pair_price, state=ForexCalcState.pair_price)

    reg_mes(handle_max_bar, state=CalculateState.max_bar)
    reg_mes(handle_min_bar, state=CalculateState.min_bar)
