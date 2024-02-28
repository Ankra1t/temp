from datetime import datetime, timedelta
from telebot import TeleBot
from telebot.types import Message

from initialize import logger

from common.utils import text_accept, set_state_data
from common.vars import DATE_FORMAT
from common.dt import get_datetime_now, get_str_by_datetime

from initialize import base_statis

from MAIN.states import AdminStatisticsState
from MAIN.callbacks import kb_statistics_back

# from initialize import kb_inl_admin, tariff_manager
# from models import Discount, Price


def handle_start_date(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    start_date = text_accept(message)

    try:
        start_date_obj = datetime.strptime(start_date, '%d.%m.%y')
    except Exception as e:
        start_date_obj = None
        logger.error(f'Ошибка handle_start_date [{e}]')

    if not start_date or not start_date_obj:
        bot.send_message(
            chat_id, '<b>Неправильный формат</b> даты начала (<b>требуется DD.MM.YY</b>), введите дату в правильном формате',
            reply_markup=kb_statistics_back())
        return

    start_date_obj -= timedelta(hours=3)

    if current_state == 'AdminStatisticsState:start_date':
        set_state_data(bot, user_id, chat_id, {
                       'start_date_obj': start_date_obj})

        bot.send_message(
            chat_id,
            "Введите дату ОКОНЧАНИЯ ПЕРИОДА в формате DD.MM.YY",
            reply_markup=kb_statistics_back()
        )

        bot.set_state(user_id, AdminStatisticsState.fin_date, chat_id)

    if current_state == 'AdminStatisticsState:start_date_only':
        start_date_filter = start_date_obj.strftime(DATE_FORMAT)
        fin_date_filter = get_datetime_now().strftime(DATE_FORMAT)

        date_start_show = get_str_by_datetime(start_date_obj)
        date_fin_show = get_str_by_datetime(get_datetime_now())

        bot.send_message(
            chat_id,
            f"Список клиентов с платежами, за выбранный период c {date_start_show} по {date_fin_show} :",
            reply_markup=None
        )
        base_statis.show_paid_users(
            message, start_to_fin=f'{start_date_filter}|{fin_date_filter}')
        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

        bot.delete_state(user_id, chat_id)


def handle_fin_date(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    fin_date = text_accept(message)
    try:
        fin_date_obj = datetime.strptime(fin_date, '%d.%m.%y')
    except Exception as e:
        fin_date_obj = None
        logger.error(f'Ошибка handle_fin_date [{e}]')

    if not fin_date or not fin_date_obj:
        bot.send_message(
            chat_id, '<b>Неправильный формат</b> даты ОКОНЧАНИЯ ПЕРИОДА (<b>требуемый DD.MM.YY</b>), введите дату в правильном формате',
            reply_markup=kb_statistics_back())
        return

    fin_date_obj -= timedelta(hours=3)

    with bot.retrieve_data(user_id, chat_id) as data:
        start_date_obj: datetime = data.get('start_date_obj')

    start_date_filter = start_date_obj.strftime(DATE_FORMAT)
    fin_date_filter = fin_date_obj.strftime(DATE_FORMAT)

    date_start_show = get_str_by_datetime(start_date_obj)
    date_fin_show = get_str_by_datetime(get_datetime_now())

    bot.send_message(
        chat_id,
        f"Список клиентов с платежами, за выбранный период c {date_start_show} по {date_fin_show} :",
        reply_markup=None
    )
    base_statis.show_paid_users(
        message, start_to_fin=f'{start_date_filter}|{fin_date_filter}')
    bot.send_message(
        chat_id,
        "Вернуться:",
        reply_markup=kb_statistics_back()
    )

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_start_date, state=AdminStatisticsState.start_date)
    reg_mes(handle_start_date, state=AdminStatisticsState.start_date_only)
    reg_mes(handle_fin_date, state=AdminStatisticsState.fin_date)
