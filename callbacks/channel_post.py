from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.states.stats import StatsState
from messages.common import transl_tr_style
from common.utils import delete_message, edit_message, set_state_data
from config_global import EN_CHANNEL_ID, RU_CHANNEL_ID
from config_logger import logger
from data.data import liteDb
from db import db
from messages.enter import msg_enter_trading_style
from models import Calculation
from Classes import calcService
from services import calculation, channel_calc

from keyboards.channel_post import (
    ChannelPostCallbackFilter, channel_post_factory,
    kb_channel_post, kb_channel_post_back_to_result, kb_channel_stat,
    kb_send_settings_calc_time, kb_send_settings_trading_style
)
from callbacks.stats import edit_channel_post

from pages.calculate import (
    send_admin_channel_calc_item,
    send_admin_channel_calc_list,
    send_admin_send_settings,
    send_calc_stat_item,
    send_calculation,
    send_stats,
    send_main
)


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = channel_post_factory.parse(call.data)
    type = data.get('type', '')
    is_calc = int(data.get('is_calc', 0))
    stat_id = int(data.get('stat_id', 0))
    page = int(data.get('page', 0))

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(f'channel_post_callback (type={type} stat_id={stat_id})')

    if type == 'main':
        send_main(call.message, bot, user_id)

    if type == 'back':
        chat_id = call.message.chat.id

        bot.delete_state(user_id, chat_id)

        msg = 'Отправка сообщений в канал'
        kb = kb_channel_post()

        bot.edit_message_text(
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

            bot.edit_message_text(
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
            bot.send_message(
                CHANNEL_ID, text
            )

    if type == 'send_settings':
        send_admin_send_settings(bot, call.message, user_id)

    if type == 'ss_stop':
        current = liteDb.getSendSettings('withoutStop')
        liteDb.updateSendSettings('withoutStop', f'{current != "True"}')
        send_admin_send_settings(bot, call.message, user_id)

    if type == 'ss_vote':
        current = liteDb.getSendSettings('isVote')
        liteDb.updateSendSettings('isVote', f'{current != "True"}')
        send_admin_send_settings(bot, call.message, user_id)

    if type == 'ss_time':
        edit_message(
            bot, call.message, 'text',
            '👉 Выберите тип периода:',
            kb_send_settings_calc_time()
        )

    if 'ss_time=' in type:
        time = type.split('=')[1]
        if time == 'none':
            time = None

        liteDb.updateSendSettings('time', time)
        send_admin_send_settings(bot, call.message, user_id)

    if type == 'ss_style':
        bot.edit_message_text(
            msg_enter_trading_style(lang),
            chat_id, mes_id,
            reply_markup=kb_send_settings_trading_style()
        )

    if 'ss_style=' in type:
        _, trading_value = type.split('=')
        value = trading_value.lower()
        if value == '**off**':
            value = None

        liteDb.updateSendSettings('style', value)
        send_admin_send_settings(bot, call.message, user_id)

    if type == 'result_cancel':
        calculation.update(
            stat_id, status='CANCEL'
        )
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            edit_channel_post(bot, stat_id)
            type = 'results'
        else:
            send_stats(bot, call.message, user_id)

    if type == 'result_deal':
        calculation.update(
            stat_id, status='DEAL'
        )

        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            edit_channel_post(bot, stat_id)
            type = 'result'
        else:
            send_stats(bot, call.message, user_id)

    if type == 'result_wait':
        calculation.update(
            stat_id, status='WAIT'
        )

        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            edit_channel_post(bot, stat_id)
            type = 'result'
        else:
            send_stats(bot, call.message, user_id)

    if 'stop+' in type or 'take+' in type:
        calc = calculation.get(stat_id)
        if calc is None:
            return

        _, value = type.split('+')
        value = float(value)

        # _, _, spot_rate = get_count_value_bet(calc)
        spot_rate = 1
        calcService.set_profit(
            stat_id,
            (-1 if 'stop+' in type else 1) *
            calc.riskValue * value * spot_rate
        )

        calculation.update(
            stat_id, status='FINISH'
        )

        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            edit_channel_post(bot, stat_id)

            if is_calc == 0:
                type = 'results'
        else:
            if is_calc == 0:
                send_stats(bot, call.message, user_id)

        if is_calc == 1:
            calc = calculation.get(stat_id)
            if calc is None:
                return
            delete_message(bot, chat_id, mes_id)
            send_calculation(bot, call.message, user_id, calc, True)

    if type == 'results':
        send_admin_channel_calc_list(bot, call.message, user_id, page=page)

    if type == 'result' or type == 'result_take' or type == 'result_stop':
        mes_type = 'take' if type == 'result_take' else 'stop' if type == 'result_stop' else ''

        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            send_admin_channel_calc_item(
                bot, call.message, user_id, stat_id, mes_type
            )
        else:
            send_calc_stat_item(
                bot, call.message, user_id, stat_id, mes_type
            )

    if type == 'comment':
        edit_message(
            bot, call.message, 'text',
            'Введите ваш комментарий:', kb_channel_post_back_to_result()
        )
        bot.set_state(user_id, StatsState.add_image_text, chat_id)
        set_state_data(bot, user_id, chat_id, {
            'stat_id': stat_id,
            'del_mes_id': call.message.id,
            'type': 'stats'
        })

    if type == 'calc':
        calc = calculation.get(stat_id)
        if calc is None:
            return

        send_calculation(bot, call.message, user_id, calc)

    if type == 'go_stats':
        send_stats(bot, call.message, user_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(ChannelPostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        channel_post=channel_post_factory.filter()
    )
