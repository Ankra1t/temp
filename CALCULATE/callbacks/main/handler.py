from datetime import timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery
from CALCULATE.callbacks.main.keyboards import kb_freeze_calc
from common.dt import get_datetime_now, get_str_by_datetime

from db_new import db_new

from .filter import main_factory, MainCallbackFilter
from ..utils import choose_first_calculate_step
from ..pages import send_settings, send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'calc':
        market = db_new.get_calculator_user_market(user_db_id) or 'crypto'
        choose_first_calculate_step(bot, user_id, call.message, market, True)

    if type == 'cancel':
        send_main(call.message, bot, user_id)

    if type == 'settings':
        send_settings(bot, call.message, user_id)

    if 'deal' in type:
        if 'not' in type:
            bot.edit_message_text(
                call.message.text or '1', chat_id, mes_id,
                reply_markup=None
            )
        else:
            bot.send_message(
                chat_id, """Вы превысили суточный процент риска ...

<b>Желаете приостановить торговлю до некоторое время?</b>

Выберите количество часов заморозки.
На это время расчеты в калькуляторе невозможно будет совершать для безопасности Вашей торговли.""",
                reply_markup=kb_freeze_calc()
            )

    if type in ['3', '6', '9', '12']:
        date = get_datetime_now() + timedelta(hours=int(type))
        bot.edit_message_text(
            f'Калькулятор заморожен до <b>{get_str_by_datetime(date)}</b>',
            chat_id, mes_id
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter())
