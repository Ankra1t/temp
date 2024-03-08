from datetime import timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new
from common.dt import get_datetime_now, get_str_by_datetime
from CALCULATE.common.messages import msg_calculate_result, msg_freeze_calc

from .keyboards import kb_deal_result, kb_freeze_calc, kb_set_calc_stats
from .filter import stats_factory, StatsCallbackFilter
from ..pages import send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = stats_factory.parse(call.data)
    type = callback_data.get('type', '')
    stat_id = int(callback_data.get('stat_id', '0'))

    user_id = call.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id


    if 'time' in type:
        _, time = type.split('+')
        date = get_datetime_now() + timedelta(hours=int(time))

        bot.edit_message_text(
            f'Калькулятор заморожен до <b>{get_str_by_datetime(date)}</b>',
            chat_id, mes_id
        )

    if 'profit' in type:
        _, profit = type.split('+')

        if profit == '':
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

            if profit == '-':
                db_new.set_calculation_in_stat(stat_id, True)
                db_new.set_calculation_profit(stat_id, -risk_value)

                bot.edit_message_text(
                    msg_freeze_calc(user_id),
                    chat_id, mes_id,
                    reply_markup=kb_freeze_calc(user_id)
                )
            elif profit != 'cancel':
                db_new.set_calculation_in_stat(stat_id, True)
                db_new.set_calculation_profit(stat_id, risk_value * int(profit))
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

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(StatsCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=stats_factory.filter())
