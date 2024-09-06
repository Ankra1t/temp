import re
from telebot.async_telebot import AsyncTeleBot

from config_logger import logger
from Classes import currencyService
from db import db
from models import MARKETS_TYPE, ForexInfo, Message, StateContext, User

from messages.errros import msg_currency_error, msg_digit_error, msg_latin_error, msg_pair_error, msg_sl_op_equal_error, msg_text_error, msg_trading_style_error
from messages.enter import (
    msg_choose_direct, msg_enter_min_bar, msg_enter_trading_style,
)

from callbacks.stats import edit_channel_post
from pages.calculate import send_calculation, create_and_send_calc
from keyboards.calculate import kb_tool, kb_calc_direct, kb_calc_cancel
from keyboards.stats import kb_deal_profit_cancel
from keyboards.settings import kb_change_currency, kb_trading_style
from pages.start import start_with_calc

from common.calc_step import choose_calculate_step
from common.utils import digit_accept, is_digit, text_accept

from states.calculate import CalculateState, ForexCalcState
from services import calculation


async def handle_tool(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id
    tool = text_accept(message)
    if tool is None or is_digit(tool):
        new_mes = await bot.send_message(
            chat_id, msg_text_error(user.lang),
            reply_markup=kb_tool(user.lang, [])
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    if not re.match(r'^[a-zA-Z0-9 ]+$', tool):
        new_mes = await bot.send_message(
            chat_id, msg_latin_error(user.lang),
            reply_markup=kb_tool(user.lang, [])
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(f'callback "handle_tool" user_tg_id={user.tgId} value={tool}')

    async with state.data() as data:
        stat_id = data.get('stat_id')
        calc_type: MARKETS_TYPE = data.get('calc_type', 'crypto')

    tool = tool.upper().replace('/', '').replace(' ', '')

    if calc_type == 'crypto':
        if tool.endswith('USDT'):
            tool = tool.replace('USDT', '')
        tool += '/USDT'

    if stat_id is None:
        await state.add_data(tool=tool)
        await choose_calculate_step(bot, message, state, user, last_value='tool')
    else:
        db.change_calculation_tool(stat_id, tool)

        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        await send_calculation(bot, message, state, user, calc_info, True)
        await state.delete()


async def handle_forex_pair(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    pair = text_accept(message)
    if pair is None or is_digit(pair):
        new_mes = await bot.send_message(chat_id, msg_pair_error(user.lang))
        await state.add_data(del_mes_id=new_mes.id)
        return

    if not re.match(r'^[a-zA-Z \/]+$', pair):
        new_mes = await bot.send_message(
            chat_id, msg_pair_error(user.lang),
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_forex_pair" user_tg_id={user.tgId} value={pair}')

    pair = pair.upper().replace(' ', '/')

    pair_arr = pair.split('/')
    if len(pair_arr) != 2 or pair_arr[0] == pair_arr[1]:
        new_mes = await bot.send_message(chat_id, msg_pair_error(user.lang))
        await state.add_data(del_mes_id=new_mes.id)
        return

    user_settings = db.get_calc_user_settings(user.id)
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
    #     state.add_data(del_mes_id=new_mes.id)
    #     return

    forex = ForexInfo(
        pair=(pair_arr[0], pair_arr[1]),
        price=(prices or {}).get(pair, 1),
        cross_prices=prices or {}
    )

    async with state.data() as data:
        stat_id = data.get('stat_id')

    if stat_id is None:
        await state.add_data(forex=forex)
        await choose_calculate_step(
            bot, message, state, user, last_value='forex'
        )
    else:
        db.change_calculation_forex(stat_id, forex)

        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        await send_calculation(bot, message, state, user, calc_info, True)
        await state.delete()


async def handle_forex_pair_price(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    user_id = message.from_user.id
    chat_id = message.chat.id

    pair_price = digit_accept(message)
    if pair_price is None:
        new_mes = await bot.send_message(chat_id, msg_pair_error(user.lang))
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_forex_pair_price" user_tg_id={user_id} value={pair_price}'
    )

    async with state.data() as data:
        forex: ForexInfo = data.get('forex', {})
        current_pair = data.get('current_pair', '')

    forex.cross_prices[current_pair] = pair_price

    await state.add_data(
        forex=forex
    )

    await state.add_data(forex=forex)
    await choose_calculate_step(
        bot, message, state, user, last_value='forex'
    )


async def handle_currency(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        new_mes = await bot.send_message(
            chat_id, msg_currency_error(user.lang),
            reply_markup=kb_change_currency(user.lang, 'calc')
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_currency" user_tg_id={user.tgId} value={value}')

    check = currencyService.getPrice('USD', value)
    if not check:
        new_mes = await bot.send_message(
            chat_id, msg_currency_error(user.lang, 'not_found'),
            reply_markup=kb_change_currency(user.lang, 'calc')
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    await state.add_data(currency=value.upper())
    await choose_calculate_step(bot, message, state, user, last_value='currency')


async def handle_deposit(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id
    mes_id = message.id

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_deposit" user_tg_id={user.tgId} value={value}')

    await state.add_data(deposit=value)
    await choose_calculate_step(bot, message, state, user, last_value='deposit')


async def handle_risk_percent(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    is_percent = False
    if message.text is not None and message.text.endswith('%'):
        is_percent = True
        message.text = message.text.replace('%', '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(user.lang)
        )
        return

    logger.info(
        f'callback "handle_risk_percent" user_tg_id={user.tgId} value={value}')

    # if value <= 0 or value >= 100:
    #     bot.send_message(
    #         chat_id,
    #         msg_percent_error(user.tgId),
    #         reply_markup=kb_calc_cancel(user.tgId)
    #     )
    #     return

    await state.add_data(risk=[value, is_percent])
    await choose_calculate_step(bot, message, state, user, last_value='risk')


async def handle_trading_style(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = text_accept(message)

    if value is None or is_digit(value):
        msg_error = f'{msg_trading_style_error(user.lang)}\n{msg_enter_trading_style(user.lang)}'
        new_mes = await bot.send_message(
            chat_id, msg_error,
            reply_markup=kb_trading_style(user.lang, 'calc')
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_trading_style" user_tg_id={user.tgId} value={value}')

    value = value.lower()

    async with state.data() as data:
        stat_id = data.get('stat_id')

    if stat_id is None:
        await state.add_data(trading_style=value)
        await choose_calculate_step(
            bot, message, state, user,
            last_value='trading_style'
        )
    else:
        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        db.change_calculation_style(stat_id, value)
        calc_info.tradingStyle = value

        await send_calculation(bot, message, state, user, calc_info, True)
        await state.delete()


async def handle_open_price(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        stat_id = data.get('stat_id')

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(
                user.lang
            ) if stat_id is None else kb_deal_profit_cancel(user.lang, stat_id)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_open_price" user_tg_id={user.tgId} value={value}'
    )

    if stat_id is None:
        await state.add_data(open_price=value)
        await choose_calculate_step(
            bot, message, state, user, last_value='open_price'
        )
    else:
        calc_info = calculation.get(stat_id)
        if calc_info is None:
            return

        if calc_info.stopLoss == value:
            new_mes = await bot.send_message(chat_id, msg_sl_op_equal_error(user.lang))
            await state.add_data(del_mes_id=new_mes.id)
            return

        db.change_calculation_open_price(stat_id, value)
        calc_info.openPrice = value

        await edit_channel_post(bot, stat_id)

        await send_calculation(bot, message, state, user, calc_info, True)
        await state.delete()


async def handle_stop_loss(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        action = data.get('action', '')
        stat_id = data.get('stat_id', '')
        open_price = data.get('open_price', '')

    stop_loss = digit_accept(message)
    if stop_loss is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(
                user.lang
            ) if stat_id is None else kb_deal_profit_cancel(user.lang, stat_id)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    if stop_loss == open_price:
        new_mes = await bot.send_message(
            chat_id, msg_sl_op_equal_error(user.lang),
            reply_markup=kb_calc_cancel(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_stop_loss" user_tg_id={user.tgId} value={stop_loss}'
    )

    if action == 'send_calc':
        await start_with_calc(bot, message, state, user, stat_id, stop_loss)
    else:
        await edit_channel_post(bot, stat_id)
        await create_and_send_calc(bot, message, state, user, stop_loss)


async def handle_stop_atr(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    stop_atr = digit_accept(message)
    if stop_atr is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_stop_atr" user_tg_id={user.tgId} value={stop_atr}'
    )

    async with state.data() as data:
        stop_type = data.get('stop_type', 'default')
        action = data.get('action', '')

    rate = 1
    if 'atr_percent' in stop_type:
        _, percent = stop_type.split('+')
        rate = float(percent) * 0.01

    new_mes = await bot.send_message(
        chat_id, msg_choose_direct(user.lang, user.tgId),
        reply_markup=kb_calc_direct(user.lang, action == 'send_calc')
    )

    await state.add_data(
        del_mes_id=new_mes.id,
        atr=abs(stop_atr) * abs(rate)
    )


async def handle_max_bar(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    max_bar = digit_accept(message)
    if max_bar is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    new_mes = await bot.send_message(
        chat_id, msg_enter_min_bar(user.lang),
        reply_markup=kb_calc_cancel(user.lang)
    )
    await state.add_data(
        max_bar=max_bar,
        del_mes_id=new_mes.id
    )
    await state.set(CalculateState.min_bar,)


async def handle_min_bar(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    min_bar = digit_accept(message)
    if min_bar is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_calc_cancel(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    async with state.data() as data:
        max_bar = data.get('max_bar', 0)
        stop_type = data.get('stop_type', 'default')
        action = data.get('action', '')

    rate = 1
    if 'atr_percent' in stop_type:
        _, percent = stop_type.split('+')
        rate = float(percent) * 0.01

    new_mes = await bot.send_message(
        chat_id, msg_choose_direct(user.lang, user.tgId),
        reply_markup=kb_calc_direct(user.lang, action == 'send_calc')
    )

    await state.add_data(
        del_mes_id=new_mes.id,
        atr=abs(max_bar - min_bar) * abs(rate)
    )


def registration(bot: AsyncTeleBot):
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
