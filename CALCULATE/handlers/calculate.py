from telebot import TeleBot
from telebot.types import Message

from config_logger import logger
from Classes import currencyService
from db import db
from models import MARKETS_TYPE, Calculation, ForexInfo

from common.utils import digit_accept, is_digit, set_state_data, text_accept
from CALCULATE.callbacks import (
    choose_calculate_step, kb_tool,
    send_calculation, kb_pair, kb_change_currency,
    kb_calc_cancel, kb_trading_style
)
from CALCULATE.states import CalculateState, ForexCalcState
from CALCULATE.common.messages import (
    msg_currency_error, msg_trading_style_error,
    msg_digit_error, msg_enter_trading_style, msg_pair_error,
    msg_pair_not_found, msg_sl_op_equal_error, msg_text_error,
)


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
        choose_calculate_step(bot, user_id, chat_id, mes_id, last_value='tool')
    else:
        db.change_calculation_tool(stat_id, tool)

        calc_info = db.get_calculation(stat_id)
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

    if prices == False and len(pairs) == 3:
        new_mes = bot.send_message(
            chat_id, msg_pair_not_found(user_id, pair),
            reply_markup=kb_pair(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

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
            bot, user_id, chat_id,
            mes_id, last_value='forex'
        )
    else:
        db.change_calculation_forex(stat_id, forex)

        calc_info = db.get_calculation(stat_id)
        if calc_info is None:
            return

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)


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
    choose_calculate_step(bot, user_id, chat_id, mes_id, last_value='currency')


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

    logger.info(f'callback "handle_tool" user_tg_id={user_id} value={value}')

    set_state_data(bot, user_id, chat_id, {'deposit': value})
    choose_calculate_step(bot, user_id, chat_id, mes_id, last_value='deposit')


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
    choose_calculate_step(bot, user_id, chat_id, mes_id, last_value='risk')


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
            bot, user_id, chat_id, mes_id,
            last_value='trading_style'
        )
    else:
        calc_info = db.get_calculation(stat_id)
        if calc_info is None:
            return

        db.change_calculation_style(stat_id, value)
        calc_info.trading_style = value

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
            bot, user_id, chat_id,
            mes_id, last_value='open_price'
        )
    else:
        calc_info = db.get_calculation(stat_id)
        if calc_info is None:
            return

        if calc_info.stop_loss == value:
            new_mes = bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
            set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
            return

        db.change_calculation_open_price(stat_id, value)
        calc_info.open_price = value

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)


def handle_stop_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    stop_loss = digit_accept(message)
    if stop_loss is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_calc_cancel(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_stop_loss" user_tg_id={user_id} value={stop_loss}')

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')

        deposit: float = data.get('deposit') or 1.0
        risk: tuple[float, bool] = data.get('risk') or (1., False)
        currency = data.get('currency', 'USD')
        trading_style = data.get('trading_style')
        trading_type = data.get('trading_type', 'margin')

        open_price = data.get('open_price') or 0
        forex = data.get('forex')
        tool = data.get('tool')
        updated_risk = data.get('updated_risk') or 1.

    if stat_id is not None:
        calc_info = db.get_calculation(stat_id)
        if calc_info is None:
            return

        if calc_info.open_price == stop_loss:
            new_mes = bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
            set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
            return

        db.change_calculation_stop_loss(stat_id, stop_loss)
        calc_info.stop_loss = stop_loss

        send_calculation(bot, message, user_id, calc_info, True)
        bot.delete_state(user_id, chat_id)
        return

    if open_price == stop_loss:
        new_mes = bot.send_message(chat_id, msg_sl_op_equal_error(user_id))
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    u_base = db.get_calc_user_settings(user_db_id)
    if u_base is None:
        return

    risk_value = risk[0]
    if risk[1]:
        risk_value *= deposit * 0.01

    calc_info = Calculation(
        user_id=user_db_id,
        deposit=deposit,
        risk_value=risk_value * updated_risk,
        open_price=open_price,
        stop_loss=stop_loss,
        round_count=u_base.round_count,
        currency=currency,
        market=u_base.market,
        tp_ratio=u_base.tp_ratio,
        split_values=u_base.split_values,
        trading_style=trading_style or None,
        tool=tool or None,
        forex_info=forex,
        trading_type=trading_type,
    )

    new_id = db.add_calculation(calc_info)
    calc_info.id = new_id

    send_calculation(bot, message, user_id, calc_info, True)

    db.minus_calculator_uses_count(user_db_id)
    db.delete_unfinished_calc_by_user(user_db_id)

    db.set_user_base(user_db_id, 'base_risk', risk[0])
    db.set_user_risk_is_percent(user_db_id, risk[1])
    db.set_user_base(user_db_id, 'base_deposit', deposit)
    db.set_user_currency(user_db_id, currency)

    bot.delete_state(user_id, chat_id)

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
