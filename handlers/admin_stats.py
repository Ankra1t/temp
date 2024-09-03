from datetime import datetime, timedelta
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio.context import StateContext

from config_logger import logger

from common.utils import text_accept
from common.vars import DATE_FORMAT
from common.dt import get_datetime_now, get_str_by_datetime

from models import Message
from Classes import base_statis

from states.admin_stats import AdminStatisticsState
from keyboards.admin_stats import kb_statistics_back


async def handle_start_date(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = await bot.get_state(user_id, chat_id)

    start_date = text_accept(message)

    try:
        start_date_obj = datetime.strptime(start_date or '', '%d.%m.%y')
    except Exception as e:
        start_date_obj = None
        logger.error(f'Ошибка handle_start_date [{e}]')

    if not start_date or not start_date_obj:
        await bot.send_message(
            chat_id, '<b>Неправильный формат</b> даты начала (<b>требуется DD.MM.YY</b>), введите дату в правильном формате',
            reply_markup=kb_statistics_back())
        return

    start_date_obj -= timedelta(hours=3)

    if current_state == 'AdminStatisticsState:start_date':
        await state.add_data(
            start_date_obj=start_date_obj
        )

        await bot.send_message(
            chat_id,
            "Введите дату ОКОНЧАНИЯ ПЕРИОДА в формате DD.MM.YY",
            reply_markup=kb_statistics_back()
        )

        await state.set(AdminStatisticsState.fin_date)

    if current_state == 'AdminStatisticsState:start_date_only':
        start_date_filter = start_date_obj.strftime(DATE_FORMAT)
        fin_date_filter = get_datetime_now().strftime(DATE_FORMAT)

        date_start_show = get_str_by_datetime(start_date_obj)
        date_fin_show = get_str_by_datetime(get_datetime_now())

        await bot.send_message(
            chat_id,
            f"Список клиентов с платежами, за выбранный период c {date_start_show} по {date_fin_show} :",
            reply_markup=None
        )
        await base_statis.show_paid_users(
            bot,
            message, start_to_fin=f'{start_date_filter}|{fin_date_filter}'
        )
        await bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

        await state.delete()


async def handle_fin_date(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    fin_date = text_accept(message)
    try:
        fin_date_obj = datetime.strptime(fin_date or '', '%d.%m.%y')
    except Exception as e:
        fin_date_obj = None
        logger.error(f'Ошибка handle_fin_date [{e}]')

    if not fin_date or not fin_date_obj:
        await bot.send_message(
            chat_id, '<b>Неправильный формат</b> даты ОКОНЧАНИЯ ПЕРИОДА (<b>требуемый DD.MM.YY</b>), введите дату в правильном формате',
            reply_markup=kb_statistics_back())
        return

    fin_date_obj -= timedelta(hours=3)

    data = state.data()
    start_date_obj: datetime = data.get('start_date_obj', {})

    start_date_filter = start_date_obj.strftime(DATE_FORMAT)
    fin_date_filter = fin_date_obj.strftime(DATE_FORMAT)

    date_start_show = get_str_by_datetime(start_date_obj)
    date_fin_show = get_str_by_datetime(get_datetime_now())

    await bot.send_message(
        chat_id,
        f"Список клиентов с платежами, за выбранный период c {date_start_show} по {date_fin_show} :",
        reply_markup=None
    )
    await base_statis.show_paid_users(
        bot,
        message, start_to_fin=f'{start_date_filter}|{fin_date_filter}'
    )
    await bot.send_message(
        chat_id,
        "Вернуться:",
        reply_markup=kb_statistics_back()
    )

    await state.delete()


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_start_date, state=AdminStatisticsState.start_date)
    reg_mes(handle_start_date, state=AdminStatisticsState.start_date_only)
    reg_mes(handle_fin_date, state=AdminStatisticsState.fin_date)
