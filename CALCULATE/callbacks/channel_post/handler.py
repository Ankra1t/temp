from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.callbacks.pages import send_main
from CALCULATE.callbacks.stats.handler import edit_channel_post
from common.utils import delete_message, edit_message
from config_global import EN_CHANNEL_ID, RU_CHANNEL_ID
from data.data import liteDb
from db import db
from models import Calculation
from CALCULATE.common.messages import msg_enter_trading_style, trading_styles_translates
from Classes import text_editor, calcService
from services import calculation, channel_calc

from .keyboards import kb_channel_post, kb_channel_stat, kb_send_settings_calc_time, kb_send_settings_trading_style
from .filter import ChannelPostCallbackFilter, channel_post_factory
from ..pages import (
    send_admin_channel_calc_item,
    send_admin_channel_calc_list,
    send_admin_send_settings,
    send_calculation
)


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = channel_post_factory.parse(call.data)
    type = data.get('type', '')
    is_calc = int(data.get('is_calc', 0))
    stat_id = int(data.get('stat_id', 0))

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

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
                    result = trading_styles_translates.get(max_style)

                    if result is None:
                        try:
                            result = str(
                                text_editor.translator.translate(
                                    max_style, 'en', 'ru'
                                ).text
                            )
                        except:
                            result = max_style
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
            msg_enter_trading_style(user_id),
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
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            channel_calc.update(
                send_data.id, status='CANCEL'
            )

        edit_channel_post(bot, stat_id)
        type = 'results'

    if type == 'result_deal':
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            channel_calc.update(send_data.id, status='DEAL')

        edit_channel_post(bot, stat_id)
        type = 'result'

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

        send_data = channel_calc.getByCalc(stat_id)
        if send_data is None:
            return
        channel_calc.update(send_data.id, status='FINISH')
        edit_channel_post(bot, stat_id)

        if is_calc == 0:
            type = 'results'
        else:
            calc = calculation.get(stat_id)
            if calc is None:
                return
            delete_message(bot, chat_id, mes_id)
            send_calculation(bot, call.message, user_id, calc, True)

    if type == 'results':
        send_admin_channel_calc_list(bot, call.message, user_id)

    if type == 'result' or type == 'result_take' or type == 'result_stop':
        mes_type = 'take' if type == 'result_take' else 'stop' if type == 'result_stop' else ''
        send_admin_channel_calc_item(bot, call.message, user_id, stat_id, mes_type)

    if type == 'calc':
        calc = calculation.get(stat_id)
        if calc is None:
            return

        send_calculation(bot, call.message, user_id, calc)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(ChannelPostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        channel_post=channel_post_factory.filter()
    )
