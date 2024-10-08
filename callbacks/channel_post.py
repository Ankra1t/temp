from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from messages.common import transl_tr_style
from common.utils import delete_message, edit_message
from config_global import EN_CHANNEL_ID, RU_CHANNEL_ID
from config_logger import logger
from data.data import liteDb
from db import db
from messages.enter import msg_enter_cancel_at, msg_enter_trading_style
from models import Calculation, CallbackQuery, StateContext, User
from Classes import calcService
from CHANNEL.channel_post import channel_post
from pages.admin import send_admin_main
from services import calculation, channel_calc, settings, ticker

from states.admin_params import AdminParamsState
from states.stats import StatsState
from keyboards.channel_post import (
    ChannelPostCallbackFilter, channel_post_factory, kb_channel_cancel_at,
    kb_channel_post, kb_channel_post_back_to_result, kb_channel_stat,
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

    if 'ch_stats' in type:
        send_datas = channel_calc.getSent() or []

        stats: list[Calculation] = []
        count_short = 0
        count_long = 0
        tools = {}
        styles = {}

        for el in send_datas:
            stat = db.get_calculation(el.id, True)
            if stat is None:
                continue

            if stat.openPrice > stat.stopLoss:
                count_long += 1
            else:
                count_short += 1

            tool = stat.tool
            if stat.forexInfo is not None:
                tool = '/'.join(stat.forexInfo.pair)

            tool = (tool or '').replace('/USDT', '')

            if tool != '':
                if tool in tools.keys():
                    tools[tool or ''] += 1
                else:
                    tools[tool or ''] = 1

            if stat.tradingStyle is None or stat.tradingStyle == '':
                pass
            elif stat.tradingStyle in styles.keys():
                styles[stat.tradingStyle] += 1
            else:
                styles[stat.tradingStyle] = 1

            stats.append(stat)

        max_tools: tuple[str, str] | None = None
        max_style: str = ''

        for el in tools.keys():
            if max_tools is None:
                max_tools = (el, '')
            elif max_tools[1] == '':
                max_tools = (max_tools[0], el)
            else:
                first_tool = max_tools[0]

                if tools[first_tool] < tools[el]:
                    max_tools = (first_tool, el)
                if tools[max_tools[1]] < tools[first_tool]:
                    max_tools = (max_tools[1], first_tool)

        for el in styles.keys():
            if max_style == '':
                max_style = el
            else:
                if styles[max_style] < styles[el]:
                    max_style = el

        count_all = len(stats)

        channels = (RU_CHANNEL_ID, EN_CHANNEL_ID)

        if 'send' not in type:
            text = f""" - {count_all} сделок
- {count_short} в шорт
- {count_long} в лонг

Чаще всего торговал: <b>{' '.join(max_tools or [])}</b>""" + (f'\nЧаще всего: <b>{max_style}</b>' if max_style else '')

            await bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_channel_stat()
            )
        else:
            for i, CHANNEL_ID in enumerate(channels):
                lang = 'ru' if i == 0 else 'en'

                if lang == 'ru':
                    text = f""" - {count_all} сделок
- {count_short} в шорт
- {count_long} в лонг

Чаще всего торговал: <b>{' '.join(max_tools or [])}</b>""" + (f'\nЧаще всего: <b>{max_style}</b>' if max_style else '')
                else:
                    result = transl_tr_style(max_style, 'en')

                    text = f""" - {count_all} deals
- {count_short} short
- {count_long} long

Most often traded: <b>{' '.join(max_tools or [])}</b>
More often: <b>{result}</b>"""
                await bot.send_message(
                    CHANNEL_ID, text
                )

    if type == 'send_settings':
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_stop':
        current = liteDb.getSendSettings('withoutStop')
        liteDb.updateSendSettings('withoutStop', f'{current != "True"}')
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'ss_vote':
        current = liteDb.getSendSettings('isVote')
        liteDb.updateSendSettings('isVote', f'{current != "True"}')
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

        liteDb.updateSendSettings('time', time)
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

        liteDb.updateSendSettings('style', value)
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
        value = float(value)

        settings.updateAdvanced(
            user.id,
            trailingStop=value
        )

        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'result_cancel':
        calculation.update(
            calc_id, status='CANCEL'
        )

        calc = calculation.get(calc_id)
        if calc is None:
            return

        send_data = channel_calc.getByCalc(calc_id)
        if send_data is not None:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice, tickerInfo and tickerInfo.price24hPcnt)
            type = 'results'
        else:
            await send_stats(bot, call.message, state, user)

    if type == 'result_deal':
        calculation.update(
            calc_id, status='DEAL'
        )

        calc = calculation.get(calc_id)
        if calc is None:
            return

        send_data = channel_calc.getByCalc(calc_id)
        if send_data is not None:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice, tickerInfo and tickerInfo.price24hPcnt)
            type = 'result'
        else:
            await send_stats(bot, call.message, state, user)

    if type == 'result_wait':
        calculation.update(
            calc_id, status='WAIT'
        )

        calc = calculation.get(calc_id)
        if calc is None:
            return

        send_data = channel_calc.getByCalc(calc_id)
        if send_data is not None:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice, tickerInfo and tickerInfo.price24hPcnt)
            type = 'result'
        else:
            await send_stats(bot, call.message, state, user)

    if 'stop+' in type or 'take+' in type:
        calc = calculation.get(calc_id)
        send_data = channel_calc.getByCalc(calc_id)
        if calc is None or (calc.ActiveCalc and not send_data):
            return

        _, value = type.split('+')
        value = float(value)

        # _, _, spot_rate = get_count_value_bet(calc)
        spot_rate = 1
        calcService.set_profit(
            calc_id,
            (-1 if 'stop+' in type else 1) *
            calc.riskValue * value * spot_rate
        )

        calc = calculation.update(
            calc_id, status='FINISH'
        )
        if not calc:
            return

        if send_data is not None:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice, tickerInfo and tickerInfo.price24hPcnt)

            if is_calc == 0:
                type = 'results'
        else:
            if is_calc == 0:
                await send_stats(bot, call.message, state, user)

        if is_calc == 1:
            calc = calculation.get(calc_id)
            if calc is None:
                return
            await delete_message(bot, chat_id, mes_id)
            await send_calculation(bot, call.message, state, user, calc, True)

    if type == 'results':
        await send_admin_channel_calc_list(bot, call.message, state, page)

    if type == 'without_stop':
        send_data = channel_calc.getByCalc(calc_id)
        if send_data:
            channel_calc.update(
                send_data.id, withoutStop=not send_data.withoutStop)
        type = 'result'

    if type == 'result' or type == 'result_take' or type == 'result_stop':
        mes_type = 'take' if type == 'result_take' else 'stop' if type == 'result_stop' else ''

        send_data = channel_calc.getByCalc(calc_id)
        if send_data is not None:
            await send_admin_channel_calc_item(
                bot, call.message, state, calc_id, mes_type
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
        calc = calculation.get(calc_id)
        if calc is None:
            return

        await send_calculation(bot, call.message, state, user, calc)

    if type == 'go_stats':
        await send_stats(bot, call.message, state, user)

    if type == 'cancel_at':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            msg_enter_cancel_at(user.lang),
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

        if time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        calc = calculation.updateCancelAt(calc_id, time)

        if calc:
            send_data = channel_calc.getByCalc(calc_id)
            if send_data is not None:
                await send_admin_channel_calc_item(
                    bot, call.message, state, calc_id
                )

    if type == 'new_stop':
        await bot.edit_message_text(
            'Введите новый стоп-лосс',
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

        calculation.updateActive(calc_id, trailingStopCount=int(value))

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

        if time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        calc = settings.updateAdvanced(user.id, cancelMinutes=time)
        await send_admin_send_settings(bot, call.message, state, user)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(ChannelPostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        channel_post=channel_post_factory.filter()
    )
