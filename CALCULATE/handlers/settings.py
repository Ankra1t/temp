import difflib
import re
from telebot import TeleBot
from telebot.types import Message

from CALCULATE.states.settings import FirstCalcState
from config_logger import logger
from db import db, BASE_VALUE_TYPE
from data.data import liteDb
from common.utils import digit_accept, is_digit, set_state_data, text_accept

from CALCULATE.callbacks import (
    kb_base_cancel, kb_splitting, kb_trading_style,
    send_settings, send_user_deposit, kb_deposit_cancel,
    kb_enter_exchange, send_exchange_settings,
    kb_change_fee, kb_choose_exchange_level, send_maker_or_taker,
    send_stop_settings, kb_after_first_settings, kb_round_count
)
from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_choose_exchange_level, msg_currency_error, msg_digit_error, msg_enter_day_risk,
    msg_enter_deposit, msg_enter_exchange_not_found,
    msg_enter_risk_percent, msg_enter_round_count, msg_enter_splitting, msg_enter_trading_style,
    msg_after_first_settings, msg_splitting_error,
    msg_success_base_set, msg_success_edit, msg_text_error
)


def handle_new_value(type: BASE_VALUE_TYPE):
    if type == 'currency':
        return

    def r_func(message: Message, bot: TeleBot):
        user_id = message.from_user.id
        user_db_id = db.get_user_id_by_tg_id(user_id)

        chat_id = message.chat.id

        is_percent = False
        if message.text is not None and message.text.endswith('%'):
            is_percent = True
            message.text = message.text.replace('%', '')

        value = digit_accept(message)
        if value is None:
            bot.send_message(
                chat_id, msg_digit_error(user_id),
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

        with bot.retrieve_data(user_id, chat_id) as data:
            action = data.get('action')

        if action == 'welcome':
            if type == 'deposit':
                bot.set_state(user_id, SettingsState.risk_percent, chat_id)
                bot.send_message(chat_id, msg_enter_risk_percent(user_id))
            else:
                bot.set_state(user_id, SettingsState.trading_style, chat_id)
                bot.send_message(
                    chat_id, msg_enter_trading_style(user_id),
                    reply_markup=kb_trading_style(user_id, 'welcome')
                )
        else:
            bot.delete_state(user_id, chat_id)
            bot.send_message(chat_id, msg_success_edit(user_id))
            send_user_deposit(bot, message, user_id, True)

    return r_func


def handle_new_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)
    if value is None or len(value) > 10:
        bot.send_message(
            chat_id, msg_currency_error(user_id),
            reply_markup=kb_deposit_cancel(user_id)
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

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    if action == 'welcome':
        bot.set_state(user_id, FirstCalcState.deposit, chat_id)
        bot.send_message(chat_id, msg_enter_deposit(user_id))
    else:
        bot.send_message(chat_id, msg_success_edit(user_id))
        send_user_deposit(bot, message, user_id, True)


def handle_splitting(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        current_tp: list[int] = data.get('take_profit', [])
        current_split: list[float] = data.get('split', [])

    enter_mes = msg_enter_splitting(user_id, current_tp, current_split)

    message.text = message.text.replace('%', '') if (
        message.text is not None) else ''

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id,
            msg_splitting_error(user_id, 'digit') + '\n' + enter_mes
        )
        return

    logger.info(
        f'callback "handle_splitting" user_tg_id={user_id} value={value}')

    if sum(current_split) + value > 100:
        bot.send_message(
            chat_id,
            msg_splitting_error(user_id, 'sum') + '\n' + enter_mes
        )
        return

    current_split.append(value)
    bot.send_message(
        chat_id, msg_enter_splitting(user_id, current_tp, current_split),
        reply_markup=kb_splitting(user_id, current_tp, current_split)
    )
    set_state_data(bot, user_id, chat_id, {'split': current_split})
    bot.set_state(user_id, SettingsState.summury_profit, chat_id)


def handle_day_risk(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)

    enter_mes = msg_enter_day_risk(user_id)
    keyboard = kb_base_cancel(user_id)

    if value is None:
        bot.send_message(
            chat_id,
            msg_text_error(user_id) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    logger.info(
        f'callback "handle_day_risk" user_tg_id={user_id} value={value}')

    is_percent = value.endswith('%')
    value = value.replace('%', '')

    if not is_digit(value):
        bot.send_message(
            chat_id,
            'Введите число\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    value = float(value)

    db.set_user_day_risk(user_db_id, value, is_percent)
    bot.send_message(chat_id, msg_success_edit(user_id))
    send_user_deposit(bot, message, user_id, True)


def handle_round_count(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = digit_accept(message, int)

    u_base = db.get_calc_user_settings(user_db_id)

    current_value = -1
    if u_base is not None:
        current_value = u_base.round_count or current_value

    enter_mes = msg_enter_round_count(user_id)
    keyboard = kb_round_count(user_id, current_value)

    if value is None:
        bot.send_message(
            chat_id,
            msg_digit_error(user_id) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    logger.info(
        f'callback "handle_round_count" user_tg_id={user_id} value={value}')

    if value < 0 or value > 5:
        bot.send_message(
            chat_id,
            msg_digit_error(user_id, 0, 5) + '\n' + enter_mes,
            reply_markup=keyboard
        )
        return

    db.set_user_round_count(user_db_id, value)
    bot.send_message(chat_id, msg_success_edit(user_id))
    send_user_deposit(bot, message, user_id, True)


def handle_trading_style(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    value = text_accept(message)

    if value is None:
        bot.send_message(
            chat_id,
            msg_text_error(user_id) + '\n' + msg_enter_trading_style(user_id),
            reply_markup=kb_base_cancel(user_id)
        )
        return

    logger.info(
        f'callback "handle_trading_style" user_tg_id={user_id} value={value}')

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action')

    db.set_user_trading_style(user_db_id, value.lower())
    bot.delete_state(user_id, chat_id)

    if action == 'welcome':
        bot.send_message(chat_id, msg_success_base_set(user_id))
    else:
        bot.send_message(chat_id, msg_success_edit(user_id))

    send_settings(bot, message, user_id, True)


def handle_first_deposit(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    match = re.match(r'[0-9]+(.*)', message.text or '')
    if match is not None:
        message.text = (message.text or '').replace(match.group(1), '')

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id)
        )
        return

    user_db_id = db.get_user_id_by_tg_id(user_id)

    db.set_user_base(user_db_id, 'deposit', value)
    db.set_user_base(user_db_id, 'risk', 1)
    db.set_user_risk_is_percent(user_db_id, True)

    u_base = db.get_calc_user_settings(user_db_id)
    if u_base is None:
        return


    bot.send_message(
        chat_id, msg_after_first_settings(
            user_id, u_base.deposit or 0, u_base.currency or '', u_base.market
        ),
        reply_markup=kb_after_first_settings(user_id)
    )


def handle_exchange(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    value = text_accept(message)
    if value is None:
        new_mes = bot.send_message(
            chat_id, msg_text_error(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
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

        new_mes = bot.send_message(
            chat_id, msg_enter_exchange_not_found(user_id, len(difflist) != 0),
            reply_markup=kb_enter_exchange(user_id, original_names)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    indexAtList = names.index(value.lower())
    exchange = exchanges[indexAtList]

    if len(exchange.fees) != 0:
        new_mes = bot.send_message(
            chat_id, msg_choose_exchange_level(user_id, exchange.fees),
            reply_markup=kb_choose_exchange_level(
                user_id, exchange.name, [fee[0] for fee in exchange.fees]
            )
        )
        return

    send_maker_or_taker(bot, message, user_id, (
        exchange.name,
        exchange.maker_fee,
        exchange.taker_fee
    ), True)


def handle_fee(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    value = digit_accept(message)
    if value is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_change_fee(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    usersExchange = liteDb.getUserExchange(user_id)

    name = ''
    if usersExchange is not None:
        name = usersExchange[0]

    liteDb.setUserExchange(user_id, (name or '', value))
    send_exchange_settings(bot, message, user_id, True)


def handle_atr_percent(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    message.text = (message.text or '').replace('%', '')

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id)
        )
        return

    liteDb.setUserStop(user_id, f'atr_percent+{value}')
    send_stop_settings(bot, message, user_id, True)


def registration(bot: TeleBot):
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

    reg_mes(handle_exchange, state=SettingsState.exchange)
    reg_mes(handle_fee, state=SettingsState.fee)

    reg_mes(handle_atr_percent, state=SettingsState.atr_percent)
