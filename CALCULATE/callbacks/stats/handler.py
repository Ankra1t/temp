from datetime import timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery
from common.utils import set_state_data

from initialize import calcService
from db import db
from common.dt import get_datetime_now, get_str_by_datetime
from CALCULATE.common.messages import msg_calculate_result, msg_calculate_saved_result, msg_calculation_saved, msg_enter_profit_minus, msg_enter_save_calc, msg_frozen
from CALCULATE.states import StatsState

from .keyboards import kb_deal_profit_minus, kb_deal_result, kb_set_calc_stats
from .filter import stats_factory, StatsCallbackFilter
from ..pages import send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = stats_factory.parse(call.data)
    type = callback_data.get('type', '')
    stat_id = int(callback_data.get('stat_id', 0))

    user_id = call.from_user.id

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if 'time' in type:
        _, time = type.split('+')
        date = get_datetime_now() + timedelta(hours=int(time))

        bot.edit_message_text(
            msg_frozen(user_id, get_str_by_datetime(date)),
            chat_id, mes_id
        )

    if 'profit' in type:
        bot.delete_state(user_id, chat_id)
        _, profit = type.split('+')

        if profit == '':
            bot.delete_message(chat_id, mes_id)
            bot.send_message(
                chat_id, msg_enter_save_calc(user_id),
                reply_markup=kb_deal_result(user_id, stat_id)
            )
        else:
            is_cancel = False

            calc_info = db.get_calculation(stat_id)
            if calc_info is None:
                return

            if profit == '-':
                bot.set_state(user_id, StatsState.loss, chat_id)
                set_state_data(bot, user_id, chat_id, {'stat_id': stat_id})
                bot.edit_message_text(
                    msg_enter_profit_minus(user_id),
                    chat_id, mes_id,
                    reply_markup=kb_deal_profit_minus(user_id, stat_id)
                )
            else:
                if profit == 'loss':
                    calcService.set_profit(stat_id, -calc_info.risk_value)
                elif profit != 'cancel':
                    pr = (
                        abs(calc_info.open_price -
                            max(calc_info.open_price +
                                (calc_info.open_price - calc_info.stop_loss) * int(profit), 0)
                            ) * calc_info.risk_value /
                        max(abs(calc_info.open_price - calc_info.stop_loss), 0.01)
                    )
                    calcService.set_profit(stat_id, pr)
                else:
                    is_cancel = True

                if is_cancel:
                    mes = msg_calculate_result(user_id, calc_info)
                    keyboard = kb_set_calc_stats(user_id, stat_id)
                else:
                    calc_info = db.get_calculation(stat_id)
                    if calc_info is None:
                        return

                    mes = msg_calculate_saved_result(user_id, calc_info)
                    mes += f'\n\n{msg_calculation_saved(user_id)}'
                    keyboard = None

                bot.edit_message_text(
                    mes, chat_id, mes_id, reply_markup=keyboard
                )

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(StatsCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=stats_factory.filter())
