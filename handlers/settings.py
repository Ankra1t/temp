import difflib
import re
from telebot.async_telebot import AsyncTeleBot

from states.settings import FirstCalcState, SettingsState

from config_logger import logger
from db import db
from models import BASE_VALUE_TYPE, Message, User, StateContext
from data.data import liteDb
from common.utils import digit_accept, is_digit, text_accept

from messages.common import msg_success_edit
from messages.errors import msg_currency_error, msg_digit_error, msg_splitting_error, msg_text_error
from messages.settings import msg_choose_exchange_level, msg_enter_exchange_not_found
from messages.main import msg_after_first_settings, msg_success_base_set
from messages.enter import (
    msg_enter_risk_percent, msg_enter_round_count, msg_enter_splitting,
    msg_enter_trading_style, msg_enter_day_risk, msg_enter_deposit,
)

from keyboards.main import kb_main
from keyboards.settings import (
    kb_base_cancel, kb_splitting, kb_trading_style,
    kb_deposit_cancel, kb_enter_exchange,
    kb_change_fee, kb_choose_exchange_level,
    kb_round_count,
)
from pages.calculate import send_settings, send_user_deposit, send_exchange_settings, send_maker_or_taker, send_atr_settings, send_stop_settings


def handle_new_value(type: BASE_VALUE_TYPE):
    if type == 'currency':
        return

    async def r_func(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
        chat_id = message.chat.id

        is_percent = False
        if message.text is not None and message.text.endswith('%'):
            is_percent = True
            message.text = message.text.replace('%', '')

        value = digit_accept(message)
        if value is None:
            await bot.send_message(
                chat_id, msg_digit_error(user.lang),
            )
            return

        logger.info(
            f'callback "handle_new_value" user_tg_id={user.tgId} value={value}')

        # if type == 'risk' and (value <= 0 or value >= 100):
        #     bot.send_message(
        #         chat_id,
        #         msg_percent_error(user.tgId),
        #         reply_markup=kb_base_cancel(user.tgId)
        #     )
        #     return

        db.set_user_base(user.id, type, value)
        if type == 'risk':
            db.set_user_risk_is_percent(user.id, is_percent)

        async with state.data() as data:
            action = data.get('action')

        if action == 'welcome':
            if type == 'deposit':
                await state.set(SettingsState.risk_percent)
                await bot.send_message(chat_id, msg_enter_risk_percent(user.lang))
            else:
                await state.set(SettingsState.trading_style)
                await bot.send_message(
                    chat_id, msg_enter_trading_style(user.lang),
                    reply_markup=kb_trading_style(user.lang, 'welcome')
                )
        else:
            await state.delete()
            await bot.send_message(chat_id, msg_success_edit(user.lang))
            await send_user_deposit(bot, message, state, user, True)

    return r_func


async def handle_new_currency(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        await bot.send_message(
            chat_id, msg_currency_error(user.lang),
            reply_markup=kb_deposit_cancel(user.lang)
        )
        return

    logger.info(
        f'callback "handle_new_currency" user_tg_id={user.id} value={value}'
    )

    # check = currencyService.getPrice('USD', value)
    # if not check:
    #     bot.send_message(
    #         chat_id, msg_currency_error(user_id, 'not_found'),
    #         reply_markup=kb_deposit_cancel(user_id)
    #     )
    #     return

    db.set_user_currency(user.id, value.upper())

    async with state.data() as data:
        action = data.get('action')

    if action == 'welcome':
        await state.set(FirstCalcState.deposit)
        await bot.send_message(chat_id, msg_enter_deposit(user.lang))
    else:
        await bot.send_message(chat_id, msg_success_edit(user.lang))
        await send_user_deposit(bot, message, state, user, True)


async def handle_splitting(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        current_tp: list[int] = data.get('take_profit', [])
        current_split: list[float] = data.get('split', [])

    enter_mes = msg_enter_splitting(user.lang, current_tp, current_split)

    message.text = message.text.replace('%', '') if (
        message.text is not None) else ''

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id,
            msg_splitting_error(user.lang, 'digit') + '\n' + enter_mes
        )
        return

    logger.info(
        f'callback "handle_splitting" user_tg_id={user.tgId} value={value}')

    if sum(current_split) + value > 100:
        await bot.send_message(
            chat_id,
            msg_splitting_error(user.lang, 'sum') + '\n' + enter_mes
        )
        return

    current_split.append(value)
    await bot.send_message(
        chat_id, msg_enter_splitting(user.lang, current_tp, current_split),
        reply_markup=kb_splitting(user.lang, current_tp, current_split)
    )
    await state.add_data(split=current_split)
    await state.set(SettingsState.summury_profit)


async def handle_day_risk(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = text_accept(message)

    enter_mes = msg_enter_day_risk(user.lang)
    keyboard = kb_base_cancel(user.lang)

    if value is None:
        await bot.send_message(
            chat_id,
            msg_text_error(user.lang) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    logger.info(
        f'callback "handle_day_risk" user_tg_id={user.tgId} value={value}')

    is_percent = value.endswith('%')
    value = value.replace('%', '')

    if not is_digit(value):
        await bot.send_message(
            chat_id,
            'Введите число\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    value = float(value)

    db.set_user_day_risk(user.id, value, is_percent)
    await bot.send_message(chat_id, msg_success_edit(user.lang))
    await send_user_deposit(bot, message, state, user, True)


async def handle_round_count(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = digit_accept(message, int)

    u_base = db.get_calc_user_settings(user.id)

    current_value = -1
    if u_base is not None:
        current_value = u_base.round_count or current_value

    enter_mes = msg_enter_round_count(user.lang)
    keyboard = kb_round_count(user.lang, current_value)

    if value is None:
        await bot.send_message(
            chat_id,
            msg_digit_error(user.lang) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    logger.info(
        f'callback "handle_round_count" user_tg_id={user.tgId} value={value}')

    if value < 0 or value > 5:
        await bot.send_message(
            chat_id,
            msg_digit_error(user.lang, 0, 5) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    db.set_user_round_count(user.id, value)
    await bot.send_message(chat_id, msg_success_edit(user.lang))
    await send_user_deposit(bot, message, state, user, True)


async def handle_trading_style(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = text_accept(message)

    if value is None:
        new_mes = await bot.send_message(
            chat_id,
            msg_text_error(user.lang) + '\n' +
            msg_enter_trading_style(user.lang),
            reply_markup=kb_base_cancel(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_trading_style" user_tg_id={user.tgId} value={value}')

    async with state.data() as data:
        action = data.get('action')

    db.set_user_trading_style(user.id, value.lower())
    await state.delete()

    if action == 'welcome':
        await bot.send_message(chat_id, msg_success_base_set(user.lang))
    else:
        await bot.send_message(chat_id, msg_success_edit(user.lang))

    await send_settings(bot, message, state, user, True)


async def handle_first_deposit(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    match = re.match(r'[0-9]+(.*)', message.text or '')
    if match is not None:
        message.text = (message.text or '').replace(match.group(1), '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang)
        )
        return

    user_db_id = db.get_user_id_by_tg_id(user.tgId)

    db.set_user_base(user_db_id, 'deposit', value)
    db.set_user_base(user_db_id, 'risk', 1)
    db.set_user_risk_is_percent(user_db_id, True)

    await bot.send_message(
        chat_id, msg_enter_risk_percent(
            user.lang, True
        ),
    )
    await state.set(FirstCalcState.risk)


async def handle_first_risk(message: Message, bot: AsyncTeleBot, user: User):
    chat_id = message.chat.id

    message.text = (message.text or '').replace('%', '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang)
        )
        return

    db.set_user_base(user.id, 'risk', value)
    db.set_user_risk_is_percent(user.id, True)

    u_base = db.get_calc_user_settings(user.id, 'crypto')
    if u_base is None:
        return

    await bot.send_message(
        chat_id, msg_after_first_settings(
            user.lang, u_base.deposit or 0,
            'USDT', u_base.market,
            (u_base.risk or (1, True))[0]
        ),
        reply_markup=kb_main(user.lang, user.tgId, is_first=True)
    )


async def handle_exchange(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = text_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_text_error(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    exchanges = liteDb.getExchanges()
    names = [el.name.lower() for el in exchanges]

    if value.lower() not in names:
        difflist = difflib.get_close_matches(value.lower(), names)
        difflist = difflist[:3]

        original_names: list[str] = []
        for el in difflist:
            indexAtList = names.index(el)
            original_names.append(exchanges[indexAtList].name)

        new_mes = await bot.send_message(
            chat_id, msg_enter_exchange_not_found(
                user.lang, len(difflist) != 0),
            reply_markup=kb_enter_exchange(user.lang, original_names)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    indexAtList = names.index(value.lower())
    exchange = exchanges[indexAtList]

    if len(exchange.fees) != 0:
        new_mes = bot.send_message(
            chat_id, msg_choose_exchange_level(user.lang, exchange.fees),
            reply_markup=kb_choose_exchange_level(
                user.lang, exchange.name, [fee[0] for fee in exchange.fees]
            )
        )
        return

    await send_maker_or_taker(
        bot, message, state, user,
        (
            exchange.name,
            exchange.maker_fee,
            exchange.taker_fee
        ),
        True
    )


async def handle_fee(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_change_fee(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    usersExchange = liteDb.getUserExchange(user.tgId)

    name = ''
    if usersExchange is not None:
        name = usersExchange[0]

    liteDb.setUserExchange(user.tgId, (name or '', value))
    await send_exchange_settings(bot, message, state, user, True)


async def handle_atr_percent(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    message.text = (message.text or '').replace('%', '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang)
        )
        return

    await state.delete()

    db.set_user_from_deposit(user.id, False)

    liteDb.setUserStop(user.tgId, f'atr_percent+{value}')
    try:
        await send_stop_settings(bot, message, state, user, True)
    except:
        pass


async def handle_atr_bars_count(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = digit_accept(message, int)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang)
        )
        return

    value = min(max(value, 2), 20)

    await state.delete()

    atr_settings = liteDb.getUserAtrSettings(user.tgId)
    bars = atr_settings[1].split('+')
    liteDb.setUserAtrSettings(
        user.tgId, (atr_settings[0], f'{bars[0]}+{value}'))

    await send_atr_settings(bot, message, state, user, True)


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_value('deposit'),
            state=SettingsState.deposit)
    reg_mes(handle_new_value('risk'),
            state=SettingsState.risk_percent)
    reg_mes(handle_day_risk,
            state=SettingsState.day_risk)
    reg_mes(handle_round_count,
            state=SettingsState.round_count)
    reg_mes(handle_trading_style,
            state=SettingsState.trading_style)

    reg_mes(handle_new_currency, state=SettingsState.currency)
    reg_mes(handle_splitting, state=SettingsState.splitting)

    reg_mes(handle_first_deposit, state=FirstCalcState.deposit)
    reg_mes(handle_first_risk, state=FirstCalcState.risk)

    reg_mes(handle_exchange, state=SettingsState.exchange)
    reg_mes(handle_fee, state=SettingsState.fee)

    reg_mes(handle_atr_percent, state=SettingsState.atr_percent)

    reg_mes(handle_atr_bars_count, state=SettingsState.atr_bars_count)
