from datetime import timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.states.calculate import CalculateState, ForexCalcState
from common.calculation import get_count_value_bet
from common.utils import delete_message, set_state_data
from common.dt import get_datetime_now, get_str_by_datetime

from config_logger import logger
from Classes import calcService, pay_guard
from db import db
from CALCULATE.common.messages import (
    msg_calculate_change, msg_calculate_delete, msg_calculate_result,
    msg_calculation_deleted, msg_enter_open_price, msg_enter_pair, msg_enter_profit_minus,
    msg_enter_save_calc, msg_enter_stop_loss, msg_enter_tool, msg_frozen, msg_market_stats, msg_enter_profit_sum,
)
from CALCULATE.callbacks import kb_main
from CALCULATE.states import StatsState
from models import MARKETS_TYPE

from .keyboards import (
    kb_calculate_change, kb_calculate_delete, kb_deal_profit_cancel,
    kb_deal_profit_minus, kb_deal_result, kb_stats
)
from .filter import stats_factory, StatsCallbackFilter
from ..pages import send_main, send_stats


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = stats_factory.parse(call.data)
    type = callback_data.get('type', '')
    stat_id = int(callback_data.get('stat_id', 0))
    stats_market: MARKETS_TYPE = callback_data.get(
        'stats_market', 'crypto'
    )  # type: ignore

    user_id = call.from_user.id

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(f'callback "settings_factory" user_tg_id={user_id} type={type} ({stats_market} {stat_id})')

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
                if 'loss' in profit:
                    rate = float(profit.replace('loss', ''))
                    _, _, spot_rate = get_count_value_bet(calc_info)
                    calcService.set_profit(bot, stat_id, -calc_info.risk_value * rate * spot_rate)
                elif profit != 'cancel':
                    _, _, spot_rate = get_count_value_bet(calc_info)
                    profit_result = calc_info.risk_value * int(profit) * spot_rate
                    calcService.set_profit(bot, stat_id, profit_result)
                else:
                    is_cancel = True

                is_valid = pay_guard.valid_use_calc(user_id)

                calc_info = db.get_calculation(stat_id)
                if calc_info is None:
                    return

                saved_stat_id = stat_id if is_cancel else -1

                stats = calcService.get_stats(user_id, calc_info.market)
                mes_calc = msg_calculate_result(
                    user_id, calc_info, None if is_cancel else stats
                )

                bot.edit_message_text(
                    mes_calc, chat_id, mes_id,
                    reply_markup=kb_main(
                        user_id, is_valid, True, saved_stat_id
                    )
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

    if type == 'go_stats':
        send_stats(bot, call.message, user_id)

    if type == 'stats_market':
        stats = calcService.get_stats(user_id, stats_market)
        text = msg_market_stats(user_id, stats_market, stats)

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_stats(user_id, 'market')
        )

    if 'delete_calc' in type:
        if '_yes' in type:
            if db.delete_calculation(stat_id):
                bot.edit_message_text(
                    msg_calculation_deleted(user_id), chat_id, mes_id
                )
                send_main(call.message, bot, user_id, True)
        elif '_no' in type:
            text = call.message.text or 'err\n'
            text = '\n'.join(text.split('\n')[:-1])

            is_valid = pay_guard.valid_use_calc(user_id)

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_main(user_id, is_valid, True, stat_id)
            )
        else:
            bot.delete_message(chat_id, mes_id)
            bot.send_message(
                chat_id,
                msg_calculate_delete(user_id, call.message.text or ''),
                reply_markup=kb_calculate_delete(user_id, stat_id)
            )

    if 'change_calc' in type:
        type_arr = type.split('+')
        kind = ''
        if len(type_arr) == 2:
            kind = type_arr[1]

        if kind == '':
            bot.edit_message_text(
                msg_calculate_change(user_id, call.message.text or ''),
                chat_id, mes_id,
                reply_markup=kb_calculate_change(user_id, stat_id)
            )
        elif kind == 'back':
            text = call.message.text or 'err\n'
            text = '\n'.join(text.split('\n')[:-1])

            is_valid = pay_guard.valid_use_calc(user_id)

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_main(user_id, is_valid, True, stat_id)
            )
        elif kind == 'open_price':
            bot.edit_message_text(
                msg_enter_open_price(user_id), chat_id, mes_id,
                reply_markup=kb_deal_profit_cancel(user_id, stat_id)
            )
            bot.set_state(user_id, CalculateState.open_price, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )
        elif kind == 'stop_loss':
            bot.edit_message_text(
                msg_enter_stop_loss(user_id), chat_id, mes_id,
                reply_markup=kb_deal_profit_cancel(user_id, stat_id)
            )
            bot.set_state(user_id, CalculateState.stop_loss, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )
        elif kind == 'tool':
            stat = db.get_calculation(stat_id)
            if stat is None:
                return

            if stat.forex_info is not None:
                state = ForexCalcState.pair
                msg = msg_enter_pair(user_id)
            else:
                state = CalculateState.tool
                msg = msg_enter_tool(user_id)

            bot.edit_message_text(
                msg, chat_id, mes_id,
                reply_markup=kb_deal_profit_cancel(user_id, stat_id)
            )
            bot.set_state(user_id, state, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(StatsCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=stats_factory.filter())
