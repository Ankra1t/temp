import re
from datetime import timedelta, datetime
from telebot import TeleBot
from telebot.types import Message
from common.dt import get_datetime_now, get_str_by_datetime

from initialize import calcService
from db_new import db_new
from common.utils import digit_accept, text_accept

from CALCULATE.states import StatsState
from CALCULATE.callbacks import kb_deal_profit_minus
from CALCULATE.common.messages import msg_calculate_result, msg_enter_profit_minus, msg_freeze_calc


def handle_loss(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id', 0)

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, 'Ошибка!\n' + msg_enter_profit_minus(user_id),
            reply_markup=kb_deal_profit_minus(user_id, stat_id)
        )
        return

    calc_info = db_new.get_calculation(stat_id)
    if calc_info is None:
        return

    mes = msg_calculate_result(user_id, calc_info)
    mes += '\n\n✅ Расчет сохранен!'

    bot.send_message(chat_id, mes)
    bot.delete_state(user_id, chat_id)

    calcService.set_profit(stat_id, -abs(value))


def handle_freeze_dt(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        mes_id = data.get('mes_id', 0)

    value = text_accept(message)
    if value is None:
        bot.send_message(
            chat_id, '✍️ Введите количество часов или "дату до" текстом',
        )
        return

    time_reg = r'^([0-1]?[0-9]|2[0-3]):[0-5]?[0-9]$'

    try:
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
            chat_id,
            (
                'Неверный формат\n '
                '✍️ Введите <i>время</i> заморозки в формате <u>ЧЧ:ММ</u>.\n'
                '✍️ Либо <i>дату до</i> в формате <u>ДД.ММ.ГГГГ ЧЧ:ММ</u>.'
            ),
        )
        return

    db_new.set_user_calc_freeze(user_db_id, finish_freeze)
    bot.send_message(
        chat_id,
        f'❄️ Калькулятор заморожен до <b>{get_str_by_datetime(finish_freeze)}</b>'
    )


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_loss, state=StatsState.loss)
    reg_mes(handle_freeze_dt, state=StatsState.freeze)
