from datetime import timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new
from common.dt import get_datetime_now, get_str_by_datetime

from .keyboards import kb_deal_result, kb_freeze_calc
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

    if type in ['3', '6', '9', '12']:
        date = get_datetime_now() + timedelta(hours=int(type))
        bot.edit_message_text(
            f'Калькулятор заморожен до <b>{get_str_by_datetime(date)}</b>',
            chat_id, mes_id
        )

    if 'profit' in type:
        _, k = type.split('+')

        if k == '':
            bot.edit_message_text(
                call.message.text or '-', chat_id, mes_id,
                reply_markup=None
            )
            bot.send_message(
                chat_id, 'Как вы закрыли данную сделку?',
                reply_markup=kb_deal_result(user_id)
            )
        elif k == '-':
            bot.edit_message_text(
                """Вы превысили суточный процент риска...

<b>Желаете приостановить торговлю на некоторое время?</b>

Выберите <i>количество часов</i> заморозки.

На это время расчеты в калькуляторе невозможно будет совершать для безопасности Вашей торговли.""",
                chat_id, mes_id,
                reply_markup=kb_freeze_calc()
            )
        else:
            send_main(call.message, bot, user_id, False, True)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter())
