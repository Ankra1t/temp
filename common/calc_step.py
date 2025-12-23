from telebot.async_telebot import AsyncTeleBot

from Classes import pay_guard
from data.data import liteDb
from db import db
from messages.calc import msg_calc_buttons_info
from models import MARKETS_TYPE, ForexInfo, Message, StateContext, User
from services import ticker

from states.calculate import CalculateState, ForexCalcState
from pages.calculate import create_and_send_calc, send_main
from keyboards.calculate import kb_calc_atr, kb_calc_cancel, kb_calc_direct, kb_pair, kb_price, kb_tool
from keyboards.settings import kb_change_currency, kb_trading_style

from messages.enter import (
    msg_choose_direct, msg_enter_atr, msg_enter_currency, msg_enter_deposit,
    msg_enter_open_price, msg_enter_pair,
    msg_enter_pair_price, msg_enter_risk_percent,
    msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style,
)


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
        'op': 'Entry price',
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


async def choose_calculate_step(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_edit=False,
    last_value: str | None = None,
):
    chat_id = message.chat.id
    mes_id = message.id

    async with state.data() as data:
        if last_value is not None:
            last_values = data.get('last_values')
            if last_values is None:
                data['last_values'] = [last_value]
            else:
                data['last_values'].append(last_value)

        calc_type: MARKETS_TYPE = data.get('calc_type', 'crypto')
        forex: ForexInfo | None = data.get('forex')
        open_price = data.get('open_price')
        trading_style = data.get('trading_style')
        tool = data.get('tool', '')
        deposit = data.get('deposit')
        currency = data.get('currency')
        risk = data.get('risk')
        updated_risk = data.get('updated_risk')
        is_try = data.get('is_try', False)
        stop_type = data.get('stop_type', 'default')
        stop_loss = data.get('stop_loss')
        atr = data.get('atr')

    is_style_change = liteDb.getStyleChange(
        user.tgId) and trading_style is None

    text = ''
    keyboard = kb_calc_cancel(user.lang)

    if currency is None:
        text += msg_enter_currency(user.lang)
        edit_to = names[user.lang]['currency']
        new_state = CalculateState.currency
        keyboard = kb_change_currency(user.lang, 'calc')

    elif calc_type == 'forex' and forex is None:
        text += msg_enter_pair(user.lang)
        edit_to = names[user.lang]['pair']
        new_state = ForexCalcState.pair
        keyboard = kb_pair(user.lang)

    elif calc_type != 'forex' and tool is None:
        text += msg_enter_tool(user.lang, calc_type, is_try)
        edit_to = names[user.lang]['tool']
        new_state = CalculateState.tool

        keyboard = kb_tool(user.lang, [])

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

        text += msg_enter_pair_price(user.lang, pair)
        edit_to = pair
        new_state = ForexCalcState.pair_price
        await state.add_data(
            current_pair=pair
        )

    elif is_style_change:
        text += msg_enter_trading_style(user.lang)
        edit_to = names[user.lang]['style']
        new_state = CalculateState.trading_style
        keyboard = kb_trading_style(user.lang, 'calc')

    elif deposit is None:
        text += msg_enter_deposit(user.lang)
        edit_to = names[user.lang]['dep']
        new_state = CalculateState.deposit

    elif risk is None:
        text += msg_enter_risk_percent(user.lang)
        edit_to = names[user.lang]['risk']
        new_state = CalculateState.risk_percent

    elif open_price is None:
        text += msg_enter_open_price(user.lang, is_try)
        edit_to = names[user.lang]['op']
        new_state = CalculateState.open_price

        op_value = None
        if calc_type == 'forex' and forex is not None:
            op_value = round(forex.price, 5)

        keyboard = kb_price(
            user.lang, user.tgId,
            updated_risk is None, op_value
        )
    elif stop_loss == -1:
        await bot.send_message(
            chat_id, msg_choose_direct(user.lang, user.tgId),
            reply_markup=kb_calc_direct(user.lang, open_price, atr)
        )
        return
    else:
        if 'atr' in stop_type:
            text += msg_enter_atr(user.lang)
            edit_to = names[user.lang]['atr']
            new_state = CalculateState.stop_atr

            atr_settings = liteDb.getUserAtrSettings(user.tgId)
            period, count = atr_settings[1].split('+')

            value = ticker.get_atr(tool, period, int(count)) or None

            if atr_settings[0] and value is not None:
                rate = 1
                if 'atr_percent' in stop_type:
                    _, percent = stop_type.split('+')
                    rate = float(percent) * 0.01

                new_atr = abs(value) * abs(rate)
                await state.add_data(
                    atr=new_atr
                )
                await bot.send_message(
                    chat_id, msg_choose_direct(user.lang, user.tgId, value),
                    reply_markup=kb_calc_direct(user.lang, open_price, new_atr)
                )
                return

            keyboard = kb_calc_atr(user.lang, user.tgId, value)
        else:
            if stop_loss is None:
                text += msg_enter_stop_loss(user.lang, is_try)
                edit_to = names[user.lang]['sl']
                new_state = CalculateState.stop_loss
            else:
                await create_and_send_calc(bot, message, state, user, stop_loss)
                if is_try:
                    await bot.send_message(
                        chat_id, msg_calc_buttons_info(user.lang)
                    )
                    liteDb.setFirstTry(user.tgId)
                return

    await state.set(new_state)

    if is_try:
        keyboard = None

    if is_edit:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard,
        )
        new_mes_id = mes_id
    else:
        new_mes = await bot.send_message(
            user.tgId, text,
            reply_markup=keyboard
        )
        new_mes_id = new_mes.id

    if not is_try:
        await state.add_data(
            del_mes_id=new_mes_id,
            edit_mes=edit_to
        )


async def choose_first_calculate_step(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    type: MARKETS_TYPE,
    is_edit=False,
    is_continue=False,
    is_try=False,
    is_channel_calc=False
):
    u_base = db.get_calc_user_settings(user.id)

    stop_type = liteDb.getUserStop(user.tgId)
    unfinished_calc = db.get_unfinished_calc_by_user(user.id)
    db.delete_unfinished_calc_by_user(user.id)

    is_from_deposit = False
    style = deposit = risk = currency = trading_type = None
    if u_base is not None:
        style = u_base.trading_style
        deposit = u_base.deposit
        currency = u_base.currency
        risk = u_base.risk
        trading_type = u_base.trading_type
        is_from_deposit = u_base.is_from_deposit

    is_style_change = liteDb.getStyleChange(user.tgId)
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
    if not (await pay_guard.valid_use_calc(user.tgId, bot)):
        await send_main(bot, message, state, user, True)
        return

    await state.delete()
    if type == 'forex':
        await state.set(ForexCalcState.pair)
    else:
        await state.set(CalculateState.tool)

    liteDb.addStartCalcCount(user.tgId)

    state_data = {
        'tool': None,
        'open_price': None,
        'stop_loss': -1 if is_channel_calc else None,

        'calc_type': type if not is_try else 'crypto',
        'stop_type': (stop_type or '') if not is_try else 'default',

        'trading_style': style if not is_try else None,
        'trading_type': trading_type if not is_try else None,
        'deposit': deposit,
        'currency': currency,
        'risk': risk,
        'is_try': is_try,
        'is_from_deposit': is_from_deposit,
    } | prev_values

    await state.add_data(
        **state_data
    )
    await choose_calculate_step(bot, message, state, user, is_edit)


async def send_calc_start(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_continue=False,
    is_try=False,
    is_edit=False,
    is_channel_calc=False
):
    u_base = db.get_calc_user_settings(user.id)
    market = u_base.market if (u_base is not None) else 'crypto'

    await choose_first_calculate_step(
        bot, message, state, user, market, is_edit, is_continue, is_try, is_channel_calc
    )
