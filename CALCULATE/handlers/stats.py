import re
from datetime import timedelta, datetime
from telebot import TeleBot
from telebot.types import Message

from config_logger import logger
from Classes import calcService
from db import db
from common.utils import delete_message, digit_accept, set_state_data, text_accept
from common.dt import get_datetime_now, get_str_by_datetime

from CALCULATE.states import StatsState
from CALCULATE.callbacks import (
    kb_deal_profit_minus, kb_calc_image,
    send_main, send_calculation, send_freeze,
    kb_calc_result,
)
from CALCULATE.common.messages import (
    msg_digit_error, msg_freeze_error, msg_frozen
)


def handle_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id', 0)

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, msg_digit_error(user_id),
            reply_markup=kb_deal_profit_minus(user_id, stat_id)
        )
        return

    logger.info(f'callback "handle_loss" user_tg_id={user_id} value={value}')

    calcService.set_profit(stat_id, -abs(value))
    calc_info = db.get_calculation(stat_id)
    if calc_info is None:
        return

    send_calculation(bot, message, user_id, calc_info, True)
    send_freeze(bot, message, user_id, calc_info.market, True)


def handle_sum(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id', 0)

    value = digit_accept(message)
    if value is None or value < 0:
        bot.send_message(
            chat_id, msg_digit_error(user_id, 0),
            reply_markup=kb_deal_profit_minus(user_id, stat_id)
        )
        return

    logger.info(f'callback "handle_sum" user_tg_id={user_id} value={value}')

    calcService.set_profit(stat_id, value)
    calc_info = db.get_calculation(stat_id)
    if calc_info is None:
        return

    send_calculation(bot, message, user_id, calc_info, True)
    send_freeze(bot, message, user_id, calc_info.market, True)


def handle_freeze_dt(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        market = data.get('market')

    value = text_accept(message) or ''

    logger.info(
        f'callback "handle_freeze_dt" user_tg_id={user_id} value={value}')

    try:
        time_reg = r'^([0-1]?[0-9]|2[0-3]):[0-5]?[0-9]$'

        if re.match(time_reg, value) is not None:
            hours, minutes = value.split(':')
            finish_freeze = get_datetime_now() + timedelta(hours=int(hours), minutes=int(minutes))
        else:
            date, time = value.split(' ')
            day, month, year = date.split('.')
            hours, minutes = time.split(':')

            if len(year) == 2:
                year = '20' + year

            finish_freeze = datetime(
                int(year), int(month), int(day),
                int(hours), int(minutes)
            ) - timedelta(hours=3)
    except:
        bot.send_message(
            chat_id, msg_freeze_error(user_id),
        )
        return

    db.set_user_calc_freeze(user_db_id, finish_freeze, market)
    bot.send_message(
        chat_id,
        msg_frozen(user_id, get_str_by_datetime(finish_freeze))
    )
    bot.delete_state(user_id, chat_id)


def handle_calc_image(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        calc_text = data.get('calc_text', 'J')
        calc_media = data.get('calc_media')
        calc_del_mes_id = data.get('calc_del_mes_id', 0)
        stat_id = data.get('stat_id', 0)

    if message.content_type != 'photo':
        delete_message(bot, chat_id, calc_del_mes_id)
        new_mes = bot.send_message(
            chat_id, calc_text,
            reply_markup=kb_calc_image(user_id, stat_id)
        )
        set_state_data(bot, user_id, chat_id, {'calc_del_mes_id': new_mes.id})
        return

    calc_text = '\n'.join(calc_text.split('\n')[:-1])
    kb = kb_calc_result(user_id, stat_id, True)

    bot.delete_message(chat_id, calc_del_mes_id)
    if calc_media is None:
        bot.edit_message_text(
            calc_text, chat_id, calc_del_mes_id,
            reply_markup=kb
        )
    else:
        bot.send_photo(
            chat_id, calc_media, calc_text,
            reply_markup=kb
        )

    bot.delete_state(user_id, chat_id)
    send_main(message, bot, user_id, True)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_sum, state=StatsState.sum)
    reg_mes(handle_loss, state=StatsState.loss)
    reg_mes(handle_freeze_dt, state=StatsState.freeze)
    reg_mes(handle_calc_image, state=StatsState.add_image)
