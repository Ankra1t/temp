import os
import re
from datetime import timedelta, datetime
from telebot import TeleBot
from telebot.types import Message

from common.calculation import get_msg_of_calc
from initialize import calcService, pay_guard, hti
from db import db
from common.utils import digit_accept, text_accept
from common.dt import get_datetime_now, get_str_by_datetime

from CALCULATE.states import StatsState
from CALCULATE.callbacks import kb_deal_profit_minus, kb_main
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

    calcService.set_profit(stat_id, -abs(value))
    calc_info = db.get_calculation(stat_id)
    if calc_info is None:
        return

    is_valid = pay_guard.valid_use_calc(user_id)

    file_path = hti.create_calculation_image(
        user_id, calc_info, True
    )
    mes = get_msg_of_calc(user_id, calc_info)

    with open(file_path, 'rb') as photo:
        bot.send_photo(
            chat_id, photo, caption=mes,
            reply_markup=kb_main(user_id, is_valid, True),
        )
    os.remove(file_path)
    bot.delete_state(user_id, chat_id)


def handle_freeze_dt(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        mes_id = data.get('mes_id', 0)

    value = text_accept(message) or ''

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

    db.set_user_calc_freeze(user_db_id, finish_freeze)
    bot.send_message(
        chat_id,
        msg_frozen(user_id, get_str_by_datetime(finish_freeze))
    )


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_loss, state=StatsState.loss)
    reg_mes(handle_freeze_dt, state=StatsState.freeze)
