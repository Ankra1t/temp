from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from common.calculation import getStrValueCount
from keyboards.stats import kb_auto_take, kb_deal_profit_cancel
from common.utils import delete_message, edit_message, get_print_float
from config_logger import logger
from messages.enter import msg_enter_auto_take, msg_enter_cancel_at, msg_enter_close_price, msg_enter_trading_style
from models import CallbackQuery, StateContext, User
from pages.admin import send_admin_main
from services import calculation

from service.user_settings_storage import user_settings_storage
from service.advanced_settings_storage import advanced_settings_storage

from states.admin_params import AdminParamsState
from states.stats import StatsState
from keyboards.channel_post import (
    ChannelPostCallbackFilter, channel_post_factory, kb_channel_cancel_at,
    kb_channel_post, kb_channel_post_back_to_result, kb_result_end,
    kb_send_settings_calc_time, kb_send_settings_cancel_hours, kb_send_settings_trading_style, kb_send_settings_trailing_stop, kb_trailing_stop
)

from pages.calculate import (
    send_admin_channel_calc_item,
    send_admin_channel_calc_list,
    send_admin_send_settings,
    send_calculation,
    send_stats,
    send_main
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    data = channel_post_factory.parse(call.data)
    type = data.get('type', '')
    is_calc = int(data.get('is_calc', 0))
    calc_id = int(data.get('stat_id', 0))
    page = int(data.get('page', 0))

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(f'channel_post_callback (type={type} calc_id={calc_id})')

    if type == 'main':
        await send_main(bot, call.message, state, user)

    if type == 'admin_main':
        await send_admin_main(bot, call.message, state)

    if type == 'back':
        chat_id = call.message.chat.id

        await state.delete()

        msg = 'Отправка сообщений в канал'
        kb = kb_channel_post()

        await bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=kb
        )

    if type == 'send_settings':
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_stop':
        current = user_settings_storage.get_send_settings('withoutStop')
        user_settings_storage.update_send_settings(
            'withoutStop', f'{current != "True"}')
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_vote':
        current = user_settings_storage.get_send_settings('isVote')
        user_settings_storage.update_send_settings(
            'isVote', f'{current != "True"}')
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_time':
        await edit_message(
            bot, call.message, 'text',
            '👉 Выберите тип периода:',
            kb_send_settings_calc_time()
        )

    if 'ss_time=' in type:
        time = type.split('=')[1]
        if time == 'none':
            time = None

        user_settings_storage.update_send_settings('time', time)
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_style':
        await bot.edit_message_text(
            msg_enter_trading_style(user.lang),
            chat_id, mes_id,
            reply_markup=kb_send_settings_trading_style()
        )

    if 'ss_style=' in type:
        _, trading_value = type.split('=')
        value = trading_value.lower()
        if value == '**off**':
            value = None

        user_settings_storage.update_send_settings('style', value)
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_tr_stop':
        await bot.edit_message_text(
            '👉 Введите значение для скользящего стопа', chat_id, mes_id,
            reply_markup=kb_send_settings_trailing_stop()
        )
        await state.set(AdminParamsState.trailing_stop)
        await state.add_data(
            del_mes_id=mes_id
        )

    if 'ss_tr_stop+' in type:
        _, value = type.split('+')

        if value == '0':
            value = None
        else:
            value = float(value)

        advanced_settings_storage.update_advanced(
            user.id,
            trailingStop=value,
            autoTake=None
        )

        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'result_cancel':
        calculation.update(
            userId=user.id, calcId=calc_id, status='CANCEL'
        )

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None:
            return

        await send_stats(bot, call.message, state, user)

    if type == 'result_deal':
        calculation.update(
            userId=user.id, calcId=calc_id, status='DEAL'
        )

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None:
            return

        await send_stats(bot, call.message, state, user)

    if type == 'result_wait':
        calculation.update(
            userId=user.id, calcId=calc_id, status='WAIT'
        )

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None:
            return

        await send_stats(bot, call.message, state, user)

    if type == 'result_end':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if not calc:
            return

        # TODO - Получения информации по монете
        ticker_info = None
        if not ticker_info or not ticker_info.indexPrice:
            return

        diffOpSl = calc.openPrice - calc.stopLoss
        valueCount = (ticker_info.indexPrice - calc.openPrice) / diffOpSl

        await bot.edit_message_text(
            f"""{calc.tool}
Закрываете по цене: {get_print_float(ticker_info.indexPrice)}
Результат: {getStrValueCount(valueCount)}""",
            chat_id, mes_id,
            reply_markup=kb_result_end(calc_id)
        )

    if type == 'result_end_yes':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if not calc or calc.status != 'DEAL':
            return

        # TODO - Получения информации по монете
        ticker_info = None
        if not ticker_info or not ticker_info.indexPrice:
            return

        diffOpSl = calc.openPrice - calc.stopLoss
        valueCount = (ticker_info.indexPrice - calc.openPrice) / diffOpSl

        calc = calculation.closeActive(
            userId=user.id, calcId=calc_id
        )

        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'result_end_no':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc:
            await send_calculation(bot, call.message, state, user, calc, is_activate=True)

    if 'stop+' in type or 'take+' in type:
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None or calc.ActiveCalc:
            return

        _, value = type.split('+')
        value = float(value)

        # TODO - Больше нет выставления результата вручную
        # _, _, spot_rate = get_count_value_bet(calc)
        # spot_rate = 1
        # calcService.set_profit(
        #     user.tgId,
        #     calc_id,
        #     (-1 if 'stop+' in type else 1) *
        #     calc.riskValue * value * spot_rate
        # )

        calc = calculation.update(
            userId=user.id, calcId=calc_id, status='FINISH'
        )
        if not calc:
            return

        if is_calc == 0:
            await send_stats(bot, call.message, state, user)

        if is_calc == 1:
            calc = calculation.get(userId=user.id, calcId=calc_id)
            if calc is None:
                return
            await delete_message(bot, chat_id, mes_id)
            await send_calculation(bot, call.message, state, user, calc, True)

    if type == 'results':
        await send_admin_channel_calc_list(bot, call.message, state, page)

    if type == 'auto_take':
        calc = calculation.get(userId=user.id, calcId=calc_id)

        takes = []
        if calc:
            diffOpSl = calc.openPrice - calc.stopLoss
            for el in range(1, 11):
                takes.append(calc.openPrice + diffOpSl * el)

        await edit_message(
            bot, call.message, 'text',
            msg_enter_auto_take(user.lang, takes),
            kb_auto_take(user.lang, calc_id)
        )

    if type == 'comment':
        await edit_message(
            bot, call.message, 'text',
            'Введите ваш комментарий:', kb_channel_post_back_to_result(calc_id)
        )
        await state.set(StatsState.add_image_text)
        await state.add_data(
            stat_id=calc_id,
            del_mes_id=call.message.id,
            type='stats'
        )

    if type == 'calc':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None:
            return

        await send_calculation(bot, call.message, state, user, calc)

    if type == 'go_stats':
        await send_stats(bot, call.message, state, user)

    if type == 'close_price':
        await state.set(StatsState.close_price)
        await bot.edit_message_text(
            msg_enter_close_price(user.lang),
            chat_id, mes_id,
            reply_markup=kb_deal_profit_cancel(user.lang, calc_id)
        )
        await state.add_data(calc_id=calc_id, del_mes_id=mes_id)

    if type == 'cancel_at':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            msg_enter_cancel_at(user.lang, True),
            kb_channel_cancel_at(calc_id)
        )
        await state.set(StatsState.cancel_at)
        await state.add_data(
            calc_id=calc_id,
            del_mes_id=new_mes_id,
            action='send_data'
        )

    if 'cancel_at+' in type:
        _, time = type.split('+')

        if time == '0':
            time = None
        elif time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        calc = calculation.updateCancelAt(
            userId=user.id, id=calc_id, minutes=time)

    if type == 'new_stop':
        await bot.edit_message_text(
            'Введите новый стоп лосс',
            chat_id, mes_id,
            reply_markup=kb_channel_post_back_to_result(calc_id)
        )
        await state.set(StatsState.new_stop)
        await state.add_data(del_mes_id=mes_id, calc_id=calc_id)

    if type == 'trailing_stop':
        await bot.edit_message_text(
            '👉 Введите значение для скользящего стопа',
            chat_id, mes_id,
            reply_markup=kb_trailing_stop(calc_id)
        )
        await state.set(AdminParamsState.trailing_stop)
        await state.add_data(
            del_mes_id=mes_id,
            calc_id=calc_id,
            type='change_sent'
        )

    if 'trailing+' in type:
        _, value = type.split('+')

        calculation.updateActive(
            userId=user.id, id=calc_id, trailingStopCount=int(value),
            autoTake=None
        )

        await send_admin_channel_calc_item(
            bot, call.message, state, calc_id
        )

    if type == 'ss_cancel_min':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            msg_enter_cancel_at(user.lang),
            kb_send_settings_cancel_hours()
        )
        await state.set(StatsState.cancel_at)
        await state.add_data(
            del_mes_id=new_mes_id,
            action='send_settings'
        )

    if 'ss_cancel_min+' in type:
        _, time = type.split('+')

        if time == '0':
            time = None
        elif time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        calc = advanced_settings_storage.update_advanced(
            user.id, cancelMinutes=time)
        await send_admin_send_settings(bot, call.message, state, user)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(ChannelPostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        channel_post=channel_post_factory.filter()
    )
