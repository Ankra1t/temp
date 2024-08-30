import difflib
import re
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from states.settings import FirstCalcState, SettingsState

from config_logger import logger
from db import db
from messages.common import msg_success_edit
from messages.errros import msg_currency_error, msg_digit_error, msg_splitting_error, msg_text_error
from messages.settings import msg_choose_exchange_level, msg_enter_exchange_not_found
from models import BASE_VALUE_TYPE
from data.data import liteDb
from common.utils import digit_accept, get_lang, is_digit, set_state_data, text_accept

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
from pages.calculate import send_settings, send_user_deposit, send_exchange_settings,send_maker_or_taker, send_atr_settings, send_stop_settings


def handle_new_value(type: BASE_VALUE_TYPE):
    if type == 'currency':
        return

    async def r_func(message: Message, bot: AsyncTeleBot):
        user_id = message.from_user.id
        user_db_id = db.get_user_id_by_tg_id(user_id)
        lang = get_lang(user_id)

        chat_id = message.chat.id

        is_percent = False
        if message.text is not None and message.text.endswith('%'):
            is_percent = True
            message.text = message.text.replace('%', '')

        value = digit_accept(message)
        if value is None:
            await bot.send_message(
                chat_id, msg_digit_error(lang),
            )
            return

        logger.info(
            f'callback "handle_new_value" user_tg_id={user_id} value={value}')

        # if type == 'risk' and (value <= 0 or value >= 100):
        #     bot.send_message(
        #         chat_id,
        #         msg_percent_error(user_id),
        #         reply_markup=kb_base_cancel(user_id)
        #     )
        #     return

        db.set_user_base(user_db_id, type, value)
        if type == 'risk':
            db.set_user_risk_is_percent(user_db_id, is_percent)

        async with bot.retrieve_data(user_id, chat_id) as data:
            action = data.get('action')

        if action == 'welcome':
            if type == 'deposit':
                await bot.set_state(user_id, SettingsState.risk_percent, chat_id)
                await bot.send_message(chat_id, msg_enter_risk_percent(lang))
            else:
                await bot.set_state(user_id, SettingsState.trading_style, chat_id)
                await bot.send_message(
                    chat_id, msg_enter_trading_style(lang),
                    reply_markup=kb_trading_style(lang, 'welcome')
                )
        else:
            await bot.delete_state(user_id, chat_id)
            await bot.send_message(chat_id, msg_success_edit(lang))
            await send_user_deposit(bot, message, user_id, True)

    return r_func


async def handle_new_currency(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)

    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        await bot.send_message(
            chat_id, msg_currency_error(lang),
            reply_markup=kb_deposit_cancel(lang)
        )
        return

    logger.info(
        f'callback "handle_new_currency" user_tg_id={user_id} value={value}'
    )

    # check = currencyService.getPrice('USD', value)
    # if not check:
    #     bot.send_message(
    #         chat_id, msg_currency_error(user_id, 'not_found'),
    #         reply_markup=kb_deposit_cancel(user_id)
    #     )
    #     return

    db.set_user_currency(user_db_id, value.upper())

    async with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    if action == 'welcome':
        await bot.set_state(user_id, FirstCalcState.deposit, chat_id)
        await bot.send_message(chat_id, msg_enter_deposit(lang))
    else:
        await bot.send_message(chat_id, msg_success_edit(lang))
        await send_user_deposit(bot, message, user_id, True)


async def handle_splitting(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)

    chat_id = message.chat.id

    async with bot.retrieve_data(user_id, chat_id) as data:
        current_tp: list[int] = data.get('take_profit', [])
        current_split: list[float] = data.get('split', [])

    enter_mes = msg_enter_splitting(lang, current_tp, current_split)

    message.text = message.text.replace('%', '') if (
        message.text is not None) else ''

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id,
            msg_splitting_error(lang, 'digit') + '\n' + enter_mes
        )
        return

    logger.info(
        f'callback "handle_splitting" user_tg_id={user_id} value={value}')

    if sum(current_split) + value > 100:
        await bot.send_message(
            chat_id,
            msg_splitting_error(lang, 'sum') + '\n' + enter_mes
        )
        return

    current_split.append(value)
    await bot.send_message(
        chat_id, msg_enter_splitting(lang, current_tp, current_split),
        reply_markup=kb_splitting(lang, current_tp, current_split)
    )
    await set_state_data(bot, user_id, chat_id, {'split': current_split})
    await bot.set_state(user_id, SettingsState.summury_profit, chat_id)


async def handle_day_risk(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)

    chat_id = message.chat.id

    value = text_accept(message)

    enter_mes = msg_enter_day_risk(lang)
    keyboard = kb_base_cancel(lang)

    if value is None:
        await bot.send_message(
            chat_id,
            msg_text_error(lang) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    logger.info(
        f'callback "handle_day_risk" user_tg_id={user_id} value={value}')

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

    db.set_user_day_risk(user_db_id, value, is_percent)
    await bot.send_message(chat_id, msg_success_edit(lang))
    await send_user_deposit(bot, message, user_id, True)


async def handle_round_count(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)

    chat_id = message.chat.id

    value = digit_accept(message, int)

    u_base = db.get_calc_user_settings(user_db_id)

    current_value = -1
    if u_base is not None:
        current_value = u_base.round_count or current_value

    enter_mes = msg_enter_round_count(lang)
    keyboard = kb_round_count(lang, current_value)

    if value is None:
        await bot.send_message(
            chat_id,
            msg_digit_error(lang) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    logger.info(
        f'callback "handle_round_count" user_tg_id={user_id} value={value}')

    if value < 0 or value > 5:
        await bot.send_message(
            chat_id,
            msg_digit_error(lang, 0, 5) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    db.set_user_round_count(user_db_id, value)
    await bot.send_message(chat_id, msg_success_edit(lang))
    await send_user_deposit(bot, message, user_id, True)


async def handle_trading_style(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)

    chat_id = message.chat.id

    value = text_accept(message)

    if value is None:
        new_mes = await bot.send_message(
            chat_id,
            msg_text_error(lang) + '\n' + msg_enter_trading_style(lang),
            reply_markup=kb_base_cancel(lang)
        )
        await set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    logger.info(
        f'callback "handle_trading_style" user_tg_id={user_id} value={value}')

    async with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    db.set_user_trading_style(user_db_id, value.lower())
    await bot.delete_state(user_id, chat_id)

    if action == 'welcome':
        await bot.send_message(chat_id, msg_success_base_set(lang))
    else:
        await bot.send_message(chat_id, msg_success_edit(lang))

    await send_settings(bot, message, user_id, True)


async def handle_first_deposit(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = get_lang(user_id)

    match = re.match(r'[0-9]+(.*)', message.text or '')
    if match is not None:
        message.text = (message.text or '').replace(match.group(1), '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(lang)
        )
        return

    user_db_id = db.get_user_id_by_tg_id(user_id)

    db.set_user_base(user_db_id, 'deposit', value)
    db.set_user_base(user_db_id, 'risk', 1)
    db.set_user_risk_is_percent(user_db_id, True)

    await bot.send_message(
        chat_id, msg_enter_risk_percent(
            lang, True
        ),
    )
    await bot.set_state(user_id, FirstCalcState.risk, chat_id)


async def handle_first_risk(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = get_lang(user_id)

    message.text = (message.text or '').replace('%', '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(lang)
        )
        return

    user_db_id = db.get_user_id_by_tg_id(user_id)

    db.set_user_base(user_db_id, 'risk', value)
    db.set_user_risk_is_percent(user_db_id, True)

    u_base = db.get_calc_user_settings(user_db_id, 'crypto')
    if u_base is None:
        return

    await bot.send_message(
        chat_id, msg_after_first_settings(
            lang, u_base.deposit or 0,
            'USDT', u_base.market,
            (u_base.risk or (1, True))[0]
        ),
        reply_markup=kb_main(lang, user_id, is_first=True)
    )


async def handle_exchange(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    lang = get_lang(user_id)

    value = text_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_text_error(lang)
        )
        await set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
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
            chat_id, msg_enter_exchange_not_found(lang, len(difflist) != 0),
            reply_markup=kb_enter_exchange(lang, original_names)
        )
        await set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    indexAtList = names.index(value.lower())
    exchange = exchanges[indexAtList]

    if len(exchange.fees) != 0:
        new_mes = bot.send_message(
            chat_id, msg_choose_exchange_level(lang, exchange.fees),
            reply_markup=kb_choose_exchange_level(
                lang, exchange.name, [fee[0] for fee in exchange.fees]
            )
        )
        return

    await send_maker_or_taker(bot, message, user_id, (
        exchange.name,
        exchange.maker_fee,
        exchange.taker_fee
    ), True)


async def handle_fee(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id

    user_id = message.from_user.id
    lang = get_lang(user_id)

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(lang),
            reply_markup=kb_change_fee(lang)
        )
        await set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    usersExchange = liteDb.getUserExchange(user_id)

    name = ''
    if usersExchange is not None:
        name = usersExchange[0]

    liteDb.setUserExchange(user_id, (name or '', value))
    await send_exchange_settings(bot, message, user_id, True)


async def handle_atr_percent(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = get_lang(user_id)

    message.text = (message.text or '').replace('%', '')

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(lang)
        )
        return

    await bot.delete_state(user_id, chat_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    db.set_user_from_deposit(user_db_id, False)

    liteDb.setUserStop(user_id, f'atr_percent+{value}')
    try:
        await send_stop_settings(bot, message, user_id, True)
    except:
        pass


async def handle_atr_bars_count(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = get_lang(user_id)

    value = digit_accept(message, int)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(lang)
        )
        return

    value = min(max(value, 2), 20)

    await bot.delete_state(user_id, chat_id)

    atr_settings = liteDb.getUserAtrSettings(user_id)
    bars = atr_settings[1].split('+')
    liteDb.setUserAtrSettings(user_id, (atr_settings[0], f'{bars[0]}+{value}'))

    await send_atr_settings(bot, message, user_id, True)


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
