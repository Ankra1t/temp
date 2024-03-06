from datetime import timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery
from CALCULATE.common.messages import msg_calculate_result

from db_new import db_new
from common.dt import get_datetime_now, get_str_by_datetime
from messages.education import calc_info

from .keyboards import kb_cancel, kb_deal_result, kb_freeze_calc, kb_set_calc_stats
from .filter import main_factory, MainCallbackFilter
from ..utils import choose_first_calculate_step
from ..pages import send_settings, send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')
    stat_id = int(callback_data.get('stat_id', '0'))

    user_id = call.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'calc':
        market = getattr(db_new.get_calc_user_settings(user_db_id), 'market', None) or 'crypto'
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
                'Как вы закрыли данную сделку?', chat_id, mes_id,
                reply_markup=kb_deal_result(user_id, stat_id)
            )
        else:
            is_cancel = False

            calc_info = db_new.get_calculation(stat_id)
            if calc_info is None:
                return

            risk_value = calc_info.risk_value

            if k == '-':
                db_new.set_calculation_in_stat(stat_id, True)
                db_new.set_calculation_profit(stat_id, -risk_value)
    #             bot.edit_message_text(
    #                 """Вы превысили суточный процент риска...

    # <b>Желаете приостановить торговлю на некоторое время?</b>

    # Выберите <i>количество часов</i> заморозки.

    # На это время расчеты в калькуляторе невозможно будет совершать для безопасности Вашей торговли.""",
    #                 chat_id, mes_id,
    #                 reply_markup=kb_freeze_calc()
    #             )
            elif k != 'cancel':
                db_new.set_calculation_in_stat(stat_id, True)
                db_new.set_calculation_profit(stat_id, risk_value * int(k))
            else:
                is_cancel = True

            mes = msg_calculate_result(user_id, calc_info)

            if is_cancel:
                mes += '\n\nХотите учесть расчеты в статистике?'
                keyboard = kb_set_calc_stats(user_id, stat_id)
            else:
                mes += '\n\n✅ Расчет сохранен!'
                keyboard = None

            bot.edit_message_text(mes, chat_id, mes_id, reply_markup=keyboard)

    if type == 'stats':
        all_stats = db_new.get_calculations_by_user(user_db_id)
        saved_stats = db_new.get_calculations_by_user(user_db_id, True)

        profit = 0
        for el in saved_stats:
            profit += el.profit or 0

        bot.edit_message_text(
            (
                f'📊 <u><b>Статистика</b></u>\n\nВсего расчетов: <b>{len(all_stats)}</b>\n'
                f'Сохраненных расчетов: <b>{len(saved_stats)}</b>\n'
                f'Общий профит: <b>{profit}</b>\n'
            ), chat_id, mes_id, reply_markup=kb_cancel(user_id)
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter())
