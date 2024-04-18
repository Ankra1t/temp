from datetime import timedelta
import os
from telebot import TeleBot
from telebot.types import CallbackQuery

from common.calculation import get_msg_of_calc
from common.utils import delete_message, set_state_data
from common.dt import get_datetime_now, get_str_by_datetime

from initialize import calcService, pay_guard, hti
from db import db
from CALCULATE.common.messages import msg_calculate_result, msg_enter_profit_minus, msg_enter_profit_sum, msg_enter_save_calc, msg_frozen
from CALCULATE.callbacks import kb_main
from CALCULATE.states import StatsState

from .keyboards import kb_deal_profit_cancel, kb_deal_profit_minus, kb_deal_result
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
            delete_message(bot, chat_id, mes_id)
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
                    diff = max(calc_info.open_price + (calc_info.open_price - calc_info.stop_loss), 0)
                    profit_result = (
                        abs(
                            calc_info.open_price - diff * int(profit)
                        ) * calc_info.risk_value /
                        max(abs(calc_info.open_price - calc_info.stop_loss), 0.00001)
                    )
                    calcService.set_profit(stat_id, profit_result)
                else:
                    is_cancel = True

                is_valid = pay_guard.valid_use_calc(user_id)

                calc_info = db.get_calculation(stat_id)
                if calc_info is None:
                    return

                saved_stat_id = stat_id if is_cancel else None

                stats = calcService.get_stats(user_id)
                mes_calc = msg_calculate_result(user_id, calc_info, stats)

                bot.edit_message_text(
                    mes_calc, chat_id, mes_id,
                    reply_markup=kb_main(
                        user_id, is_valid, True, saved_stat_id or -1)
                )
                # file_path = hti.create_calculation_image(
                #     user_id, calc_info, not is_cancel
                # )

                # with open(file_path, 'rb') as photo:
                #     bot.delete_message(chat_id, mes_id)
                #     bot.send_photo(
                #         chat_id, photo, caption=mes,
                #         reply_markup=kb_main(
                #             user_id, is_valid, True, saved_stat_id
                #         ),
                #     )
                # os.remove(file_path)
                bot.delete_state(user_id, chat_id)

    if type == 'sum':
        bot.set_state(user_id, StatsState.sum, chat_id)
        set_state_data(bot, user_id, chat_id, {'stat_id': stat_id})
        bot.edit_message_text(
            msg_enter_profit_sum(user_id),
            chat_id, mes_id,
            reply_markup=kb_deal_profit_cancel(user_id, stat_id)
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
