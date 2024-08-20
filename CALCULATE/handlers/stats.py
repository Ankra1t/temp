import re
from datetime import timedelta, datetime
from telebot import TeleBot
from telebot.types import Message

from CALCULATE.callbacks.main.keyboards import kb_violation_skip
from CALCULATE.callbacks.pages import send_admin_channel_calc_item, send_admin_channel_calc_list, send_stats, send_violation
from CALCULATE.callbacks.stats.handler import edit_channel_post
from CALCULATE.states.settings import ViolationState
from CALCULATE.states.stats import ChannelCalcState
from config_logger import logger
from Classes import calcService
from db import db
from common.utils import delete_message, digit_accept, set_state_data, text_accept
from common.dt import get_datetime_now, get_str_by_datetime

from CALCULATE.states import StatsState
from CALCULATE.callbacks import (
    kb_deal_profit_minus, kb_calc_image_text,
    send_calculation, send_freeze,
    send_confirm_calc_send
)
from CALCULATE.common.messages import (
    msg_digit_error, msg_freeze_error, msg_frozen, msg_text_error
)
from services import calculation, channel_calc, violation


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
    calc_info = calculation.get(stat_id)
    if calc_info is None:
        return

    calculation.update(
        stat_id, status='FINISH'
    )

    send_data = channel_calc.getByCalc(stat_id)
    if send_data is not None:
        edit_channel_post(bot, stat_id)

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
    calc_info = calculation.get(stat_id)
    if calc_info is None:
        return

    calculation.update(
        stat_id, status='FINISH'
    )

    send_data = channel_calc.getByCalc(stat_id)
    if send_data is not None:
        edit_channel_post(bot, stat_id)

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


def handle_calc_image_text(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        calc_text = data.get('calc_text', 'J')
        stat_id = data.get('stat_id', 0)
        type = data.get('type', '')

    delete_message(bot, chat_id, message.id)

    if message.content_type != 'photo' and message.content_type != 'text':
        new_mes = bot.send_message(
            chat_id, calc_text,
            reply_markup=kb_calc_image_text(user_id, stat_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    text = message.html_caption or message.html_text
    photo = None
    if message.photo is not None:
        photo = message.photo[0].file_id

    data = {}

    calc = calculation.get(stat_id)
    if calc is None:
        return

    if photo:
        data['photo'] = photo

    if text:
        if calc.status == 'FINISH' or type == 'stats':
            now = get_datetime_now() + timedelta(hours=3)
            data['comment'] = (
                (calc.comment or '') +
                f'\n<b>{now.strftime("%H:%M")}</b> - '
                + text
            ).strip()
        else:
            data['description'] = text

    calc = calculation.update(
        stat_id,
        **data
    )
    if calc is None:
        return

    bot.delete_state(user_id, chat_id)

    if type != 'stats':
        send_calculation(bot, message, user_id, calc, True)
    else:
        send_data = channel_calc.getByCalc(calc.id)
        if send_data:
            edit_channel_post(bot, calc.id)

        send_admin_channel_calc_item(
            bot, message, user_id, stat_id, is_first=True
        )


def handle_send_text(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    new_text = message.html_text
    if new_text is None:
        new_mes = bot.send_message(
            chat_id, 'Введите текст:'
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data['stat_id']

    calculation.update(stat_id, description=new_text)

    bot.delete_state(user_id, chat_id)
    send_confirm_calc_send(bot, message, stat_id, True)


def handle_send_photo(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    new_photo = message.photo[0] \
        if message.photo is not None and len(message.photo) > 0 \
        else None

    if new_photo is None:
        new_mes = bot.send_message(
            chat_id, 'Отправьте фото:'
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data['stat_id']

    calculation.update(stat_id, photo=new_photo.file_id)

    bot.delete_state(user_id, chat_id)
    send_confirm_calc_send(bot, message, stat_id, True)


def handle_channel_calc_loss(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id')
        is_calc = data.get('is_calc')
        type = data.get('type')

    value = digit_accept(message)
    if value is None:
        new_mes = bot.send_message(
            chat_id, msg_digit_error(0),
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    calcService.set_profit(stat_id, abs(value) * (-1 if type == 'stop' else 1))
    calc = calculation.get(stat_id)
    if calc is None:
        return

    calculation.update(
        stat_id, status='FINISH'
    )

    bot.delete_state(user_id, chat_id)
    send_data = channel_calc.getByCalc(stat_id)
    if send_data is not None:
        edit_channel_post(bot, stat_id)

        if is_calc:
            send_calculation(bot, message, user_id, calc, True)
        else:
            send_admin_channel_calc_list(bot, message, user_id, True)
    else:
        if is_calc:
            send_calculation(bot, message, user_id, calc, True)
        else:
            send_stats(bot, message, user_id, True)


def handle_violation_message(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        violation_id = data.get('violation_id', 0)

    if message.content_type != 'photo' and message.content_type != 'text':
        new_mes = bot.send_message(
            chat_id, msg_text_error(user_id),
            reply_markup=kb_violation_skip(user_id)
        )
        set_state_data(bot, user_id, chat_id, {'del_mes_id': new_mes.id})
        return

    text = message.html_caption or message.html_text
    photo = None
    if message.photo is not None:
        photo = message.photo[0].file_id

    violation.update(
        violation_id,
        text,
        photo
    )

    bot.delete_state(user_id, chat_id)
    send_violation(bot, message, user_id, is_first=True)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_sum, state=StatsState.sum)
    reg_mes(handle_loss, state=StatsState.loss)
    reg_mes(handle_freeze_dt, state=StatsState.freeze)
    reg_mes(handle_calc_image_text, state=StatsState.add_image_text)

    reg_mes(handle_send_text, state=StatsState.send_add_text)
    reg_mes(handle_send_photo, state=StatsState.send_add_photo)

    reg_mes(handle_channel_calc_loss, state=ChannelCalcState.loss)
    reg_mes(handle_violation_message, state=ViolationState.message)
