import os
from telebot.types import Message, InputMediaPhoto
from telebot import TeleBot

from MAIN.common.messages import msg_user_tariff
from common.utils import delete_message, edit_message, get_lang, set_state_data
from db import db
from data.data import liteDb

from Classes import pay_guard, calcService, hti
from CALCULATE.states import StatsState
from CALCULATE.common.messages import (
    msg_calculation, msg_change_style_settings, msg_channel_calculation, msg_deposit, msg_dop_settings, msg_exchange,
    msg_freeze_calc, msg_main, msg_main_freeze, msg_maker_or_taker,
    msg_no_uses, msg_settings, msg_manual, msg_sl_op_equal_error,
    msg_stats_page, msg_stop_page, msg_summury_profit_settings
)

from messages.users import msg_choose_tariff_type, msg_no_tariffs
from models import MARKETS_TYPE, Calculation

from .manual.keyboards import kb_manual
from .main.keyboards import kb_main
from .settings.keyboards import (
    kb_change_deposit, kb_change_style_settings, kb_choose_stop_type, kb_dop_settings, kb_exchange,
    kb_maker_or_taker, kb_settings, kb_summury_profit,
)
from .stats.keyboards import kb_confirm_channel_post, kb_freeze_calc, kb_stats
from .tariff.keyboards import kb_choose_products, kb_tariff_list, kb_user_tariff_back


def send_main(message: Message, bot: TeleBot, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)
    liteDb.addPagesCount(user_id)

    is_rus = bot.get_chat_member(chat_id, user_id).user.language_code == 'ru'
    is_valid_use = pay_guard.valid_use_calc(user_id, bot)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    uses_count = db.get_calculator_uses_count(user_db_id) or 0
    freeze_dt = db.get_user_calc_freeze(user_db_id)
    unfinished_calc = db.get_unfinished_calc_by_user(user_db_id)

    if is_valid_use:
        text = msg_main(user_id, uses_count, True)
    elif freeze_dt is not None:
        text = msg_main_freeze(user_id, freeze_dt)
    else:
        text = msg_no_uses(user_id)

    keyboard = kb_main(user_id, is_valid_use, None,
                       unfinished_calc is not None)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        edit_message(
            bot, message, 'text', text, keyboard
        )


def send_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)
    liteDb.addPagesCount(user_id)

    is_risk_update = liteDb.getRiskUpdate(user_id)

    msg = msg_settings(user_id, is_risk_update)
    markup = kb_settings(user_id)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        edit_message(bot, message, 'text', msg, markup)


def send_dop_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calc_output = db.get_user_calc_output(user_db_id)
    is_risk_update = liteDb.getRiskUpdate(user_id)

    msg = msg_dop_settings(user_id, calc_output, is_risk_update)
    markup = kb_dop_settings(user_id, calc_output, is_risk_update)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        edit_message(bot, message, 'text', msg, markup)


def send_exchange_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    exchange = liteDb.getUserExchange(user_id)

    msg = msg_exchange(user_id, exchange)
    markup = kb_exchange(user_id, exchange is not None)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        edit_message(bot, message, 'text', msg, markup)


def send_trading_style_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    style = '-'
    if u_base is not None:
        style = u_base.trading_style or style

    is_style_change = liteDb.getStyleChange(user_id)

    msg = msg_change_style_settings(user_id, style, is_style_change)
    markup = kb_change_style_settings(user_id, is_style_change)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        edit_message(bot, message, 'text', msg, markup)


def send_maker_or_taker(bot: TeleBot, message: Message, user_id: int, info: tuple[str, float, float], is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    msg = msg_maker_or_taker(user_id, info[1], info[2])
    markup = kb_maker_or_taker(user_id, *info)

    if is_first:
        bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        edit_message(bot, message, 'text', msg, markup)


def send_user_deposit(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    market = db.get_user_current_market(user_db_id)
    u_base = db.get_calc_user_settings(user_db_id)

    is_update = False
    if u_base is not None:
        is_update = u_base.is_updating_deposit

    text = msg_deposit(user_id)
    keyboard = kb_change_deposit(user_id, is_update, market)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


def send_manual_page(message: Message, bot: TeleBot, page: int, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_manual[page - 1]
    photo = open(f'src/img/info_calc/{page}.jpg', 'rb')
    keyboard = kb_manual(user_id, page, len(msg_manual))

    if is_first:
        bot.send_photo(
            chat_id, photo, text, 'MarkDown',
            reply_markup=keyboard
        )
    else:
        bot.edit_message_media(
            InputMediaPhoto(photo, text, 'MarkDown'),
            chat_id, mes_id,
            reply_markup=keyboard
        )


def send_summury_profit_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_summury_profit_settings(user_id)
    kb = kb_summury_profit(user_id)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=kb
        )
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


def send_stats(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)
    liteDb.addPagesCount(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calcs = db.get_calculations_by_user(user_db_id)

    text = msg_stats_page(user_id, len(calcs))
    kb = kb_stats(user_id)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=kb
        )
    else:
        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


def send_user_tariffs(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    text = msg_choose_tariff_type(user_id)
    keyboard = kb_choose_products(user_id)

    if is_first:
        bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        edit_message(
            bot, message, 'text', text, keyboard
        )


def send_tariffs_list_item(
    bot: TeleBot,
    message: Message,
    user_id: int,
    tariff_type: str,
    page: int,
    is_first=False,
    is_rus=False
):
    chat_id = message.chat.id
    mes_id = message.id

    tariffs = db.get_prices_by_product(tariff_type, True, True)
    count = len(tariffs)

    if count == 0:
        bot.edit_message_text(
            msg_no_tariffs(user_id), chat_id, mes_id,
            reply_markup=kb_user_tariff_back(user_id)
        )
    else:
        tariff = tariffs[page]
        tariff_id = tariff.id or 0

        lang = get_lang(user_id)

        if lang == 'ru':
            image = tariff.img
        else:
            image = tariff.img_en or tariff.img

        text = msg_user_tariff(user_id, tariff)
        keyboard = kb_tariff_list(
            user_id, tariff_id, count, tariff_type, page, is_rus)

        def send():
            if image is None:
                bot.send_message(chat_id, text, reply_markup=keyboard)
            else:
                bot.send_photo(
                    chat_id, image, '',
                    reply_markup=keyboard
                )

        if is_first:
            send()
        elif message.content_type == 'photo' and image is not None:
            bot.edit_message_media(
                InputMediaPhoto(image, '', 'HTML'), chat_id, mes_id,
                reply_markup=keyboard
            )
        elif message.content_type == 'text' and image is None:
            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )
        else:
            delete_message(bot, chat_id, mes_id)
            send()


def send_calculation(
    bot: TeleBot,
    message: Message,
    user_id: int,
    calc: Calculation,
    is_first=False,
    is_try=False
):
    chat_id = message.chat.id
    mes_id = message.id

    bot.delete_state(user_id, chat_id)

    is_access = pay_guard.valid_use_calc(user_id, bot)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calc_output = db.get_user_calc_output(user_db_id)

    kb = kb_main(user_id, is_access, calc, is_try=is_try)

    if calc_output == 'text' or is_try:
        text = msg_calculation(user_id, calc, is_try)

        if is_first:
            bot.send_message(chat_id, text, reply_markup=kb)
        else:
            edit_message(bot, message, 'text', text, kb)
    else:
        file_path, caption = hti.create_calculation_image(
            user_id, calc
        )

        with open(file_path, 'rb') as photo:
            if not is_first:
                bot.delete_message(chat_id, mes_id)
            bot.send_photo(
                chat_id, photo, caption=caption,
                reply_markup=kb,
            )
        os.remove(file_path)


def send_freeze(
    bot: TeleBot,
    message: Message,
    user_id: int,
    market: MARKETS_TYPE,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    day_risk = calcService.check_day_risk(user_id, market)
    if day_risk:
        bot.set_state(user_id, StatsState.freeze, chat_id)
        set_state_data(bot, user_id, chat_id, {'market': market})

        text = msg_freeze_calc(user_id, day_risk)
        kb = kb_freeze_calc(user_id)

        if is_first:
            bot.send_message(
                chat_id, text,
                reply_markup=kb,
            )
        else:
            edit_message(bot, message, 'text', text, kb)


def send_confirm_calc_send(bot: TeleBot, message: Message, stat_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    stat = db.get_calculation(stat_id)
    send_data = liteDb.getSendCalc(stat_id)
    if stat is None or send_data is None:
        return

    photo = send_data.photo
    text = msg_channel_calculation(stat, 'ru', send_data.without_stop, send_data.time or '')\
        + (f'\n{send_data.text}\n' if send_data.text is not None else '')

    text += '\nОпрос: ' + ('✅' if send_data.is_vote else '❌')

    kb = kb_confirm_channel_post(
        stat_id
    )

    if is_first:
        if photo is None:
            bot.send_message(
                chat_id, text,
                reply_markup=kb
            )
        else:
            bot.send_photo(
                chat_id,
                photo, text,
                reply_markup=kb
            )
    else:
        edit_message(
            bot,
            message, 'text' if photo is None else 'photo',
            text, kb, photo
        )


def create_and_send_calc(bot: TeleBot, message: Message, user_id: int, stop_loss: float):
    chat_id = message.chat.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')
        calc_type = data.get('calc_type', 'crypto')

        deposit: float = data.get('deposit') or 1.0
        risk: tuple[float, bool] = data.get('risk') or (1., False)
        currency = data.get('currency', 'USD')
        trading_style = data.get('trading_style')
        trading_type = data.get('trading_type', 'margin')

        open_price: float = data.get('open_price') or 0
        forex = data.get('forex')
        tool = data.get('tool')
        updated_risk = data.get('updated_risk') or 1.
        is_from_deposit = data.get('is_from_deposit') or False

        is_try = data.get('is_try', False)

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

    if is_from_deposit:
        count_bet = deposit / open_price
        risk_value = count_bet * abs(open_price - stop_loss)
    else:
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
        market=calc_type,
        tp_ratio=u_base.tp_ratio,
        split_values=u_base.split_values,
        trading_style=trading_style or None,
        tool=tool or None,
        forex_info=forex,
        trading_type=trading_type,
        is_from_deposit=is_from_deposit
    )

    if not is_try:
        new_id = db.add_calculation(calc_info)
        calc_info.id = new_id

        userExchange = liteDb.getUserExchange(user_id)
        if userExchange is not None:
            liteDb.addCalc(new_id, userExchange[0], userExchange[1])

        db.minus_calculator_uses_count(user_db_id)
        db.delete_unfinished_calc_by_user(user_db_id)

        db.set_user_base(user_db_id, 'risk', risk[0])
        db.set_user_risk_is_percent(user_db_id, risk[1])
        db.set_user_base(user_db_id, 'deposit', deposit)
        db.set_user_currency(user_db_id, currency)
    else:
        liteDb.setFirstTry(user_id)

    send_calculation(bot, message, user_id, calc_info, True, is_try)

    bot.delete_state(user_id, chat_id)


def send_stop_settings(bot: TeleBot, message: Message, user_id: int, is_first=False):
    chat_id = message.chat.id
    mes_id = message.id

    stop_type = liteDb.getUserStop(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    current_fd = False
    if u_base is not None:
        current_fd = u_base.is_from_deposit

    mes = msg_stop_page(user_id, stop_type, current_fd)
    kb = kb_choose_stop_type(user_id, current_fd)

    if is_first:
        bot.send_message(
            chat_id, mes,
            reply_markup=kb
        )
    else:
        bot.edit_message_text(
            mes, chat_id, mes_id,
            reply_markup=kb
        )
