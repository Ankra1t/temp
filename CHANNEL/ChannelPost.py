from random import randint
from typing import Literal, Optional
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import InputPollOption

from common.calculation import getTrailingStopsMessage
from common.dt import get_datetime_now, get_str_by_datetime
from config_global import EN_CHANNEL_ID, RESULTS_CHANNEL_ID, RESULTS_CHANNEL_NAME, RU_CHANNEL_ID, SITE_URL, TOURNAMENT_CHANNEL_ID
from config_logger import logger
from messages.common import transl_status
from models import CALC_STATUS_TYPE, Calculation, Live, SendCalc, SentMessages
from services import calculation, channel_calc

from common.utils import antiflood, get_print_float
from common.calculation import getStrValueCount
from messages.calc import msg_channel_calc, months


class ChannelPost():
    def __init__(self, bot: AsyncTeleBot, main_bot: AsyncTeleBot):
        self.main_bot = main_bot
        self.bot = bot

        self.channels = [str(el) for el in (RU_CHANNEL_ID, EN_CHANNEL_ID)]
        self.langs: list[Literal['ru', 'en']] = ['ru', 'en']
        self.tournament_channel = TOURNAMENT_CHANNEL_ID

        self.stats_channel = str(RESULTS_CHANNEL_ID)
        self.loading_vote_message_ids: dict[int, tuple[int, int]] = {}

    async def send_calc(
        self,
        calc: Calculation,
        send_data: SendCalc | None,
        indexPrice: Optional[float],
        percent24h: Optional[float],
        updateLive=True,
    ):
        if send_data is None:
            weekMessages = None
        else:
            weekMessages = channel_calc.getSentMessagesByCalc(calc.id)

        if send_data is None:
            if calc.ActiveCalc and calc.ActiveCalc.chMesIds:
                chId, mesId = calc.ActiveCalc.chMesIds.split('+++')
                chIds = [int(chId)]
                mesIds = [mesId]
                langs = ['ru']
            else:
                chIds = [self.tournament_channel]
                langs: list[Literal['ru', 'en']] = ['ru']
                mesIds = None
        else:
            if send_data.messages is not None:
                chIds = send_data.messages.chIds
                mesIds = send_data.messages.mesIds
                langs = send_data.messages.langs
            else:
                chIds = self.channels
                langs = self.langs
                mesIds = None

        newMesIds = []

        for chId_i, chId in enumerate(chIds):
            lang = langs[chId_i]

            if send_data is None:
                mesNum = -1
            elif weekMessages:
                mesNum = weekMessages.mesNum or 1
            else:
                mesNum = 1

            if send_data is None:
                withoutStop = False
                time = None
            else:
                withoutStop = send_data.withoutStop
                time = send_data.time

            trader_mes = ''
            if send_data is None:
                stats = calculation.getActiveStatsByUser(
                    userId=calc.userId, id=calc.userId)
                if stats:
                    name = f'@{stats.user.tgUsername}' if stats.user.tgUsername else stats.user.tgId

                    profit = getStrValueCount(stats.data.profitCount, lang)

                    trader_mes = f"""⚡️ Трейдер: {name}
За марафон: {get_print_float(stats.data.longCount + stats.data.shortCount)} сделок
{get_print_float(stats.data.longCount)} long / {get_print_float(stats.data.shortCount)} short
Результат сейчас: {profit}"""

            msg = msg_channel_calc(
                calc, lang, withoutStop, time or '',
                mesNum, indexPrice, percent24h,
                try_link=f'https://t.me/{(await self.main_bot.get_me()).username}?start=calc_{calc.id}',
                isActiveCalc=send_data is None,
                traderMes=trader_mes
            )

            try:
                if mesIds is not None:
                    if calc.photo is None:
                        await antiflood(
                            self.bot.edit_message_text,
                            msg, chId, int(mesIds[chId_i]),
                            disable_web_page_preview=True
                        )
                    else:
                        await antiflood(
                            self.bot.edit_message_caption,
                            msg, chId, int(mesIds[chId_i])
                        )
                else:
                    if calc.photo is None:
                        new_mes = await antiflood(
                            self.bot.send_message,
                            chId, msg,
                            disable_web_page_preview=True
                        )
                    else:
                        if '_calc_' in calc.photo:
                            photo = SITE_URL + '/uploads/' + calc.photo
                        else:
                            photo = calc.photo

                        new_mes = await antiflood(
                            self.main_bot.send_photo,
                            chId, calc.photo, msg,
                        )

                    newMesIds.append(str(new_mes.id))
            except ApiTelegramException as e:
                if e.error_code != 400 or 'message is not modified' not in e.result_json["description"]:
                    logger.error(
                        f'CALC SEND ERROR (ID {calc.id}): {e.error_code} {e.description}')

        if len(newMesIds) == len(chIds):
            if send_data is None:
                a = calculation.updateActive(
                    userId=1,
                    id=calc.id,
                    chMesIds=f'{chIds[0]}+++{newMesIds[0]}'
                )
                print(a)
            else:
                channel_calc.update(
                    send_data.id,
                    sent=True,
                    messages={
                        'chIds': chIds,
                        'mesIds': newMesIds,
                        'langs': langs,
                    }
                )

        if updateLive and send_data:
            await self.send_stats(calc.id)

    async def send_live(
        self,
        live: Live,
    ):
        new_live_mes_ids = []

        if live.messages is not None:
            chIds = live.messages.chIds
            mesIds = live.messages.mesIds
            langs = live.messages.langs
        else:
            chIds = self.channels
            langs = self.langs
            mesIds = None

        for calc_ in live.toUpdate:
            await self.send_calc(calc_.calc, calc_.sendData, calc_.indexPrice, calc_.percent24h, False)

        for chId_i, chId in enumerate(chIds):
            lang = langs[chId_i]

            msges = ''
            in_deal_value_count = 0

            for calc_ in live.deal:
                current_msg = ''

                calcMesId = None
                if calc_.messages is not None:
                    calcMesId = calc_.messages.mesIds[chId_i]

                comment = calc_.comment
                trailing_stops = getTrailingStopsMessage(
                    lang, calc_.TrailingStops, calc_.openPrice, calc_.stopLoss
                )

                result = ''
                if calc_.takeProfitRatio:
                    result = getStrValueCount(calc_.takeProfitRatio, lang)
                    in_deal_value_count += calc_.takeProfitRatio
                else:
                    result = 'В сделке' if lang == 'ru' else 'In deal'
                    result = f'<b>{result}</b>'

                tool = f'{(calc_.tool or "").replace("/USDT", "")}'
                if calcMesId is not None:
                    tool = f'<a href="https://t.me/c/{str(chId).replace("-100", "")}/{calcMesId}">{tool}</a>'

                price = ''
                take_profit = ''
                if calc_.indexPrice is not None:
                    price = get_print_float(
                        calc_.indexPrice, 0 if calc_.indexPrice > 100 else 4
                    )
                    price = f' {price}'

                current_msg += f'\n<b>{tool}</b>{price} | {result}'
                current_msg += take_profit

                if lang == 'ru' and comment is not None:
                    current_msg += f'\n{comment.strip()}'

                if trailing_stops != '':
                    current_msg += trailing_stops

                # if finishAt is not None and valueCount is not None:
                #     current_msg += f'\n{finishAt.strftime("%H:%M")} - '
                #     current_msg += 'сделка закрыта' if lang == 'ru' else 'deal closed'

                #     tp_sl = ''
                #     if valueCount > 0:
                #         tp_sl = 'тейк' if lang == 'ru' else 'take'
                #     else:
                #         tp_sl = 'стоп' if lang == 'ru' else 'stop'

                #     current_msg += f' ({get_print_float(valueCount, 1)} {tp_sl})'

                msges += current_msg

            finished = ''
            for calc_ in live.finished:
                valueCount = calc_.valueCount

                result = getStrValueCount(valueCount, lang)

                tool = f'{(calc_.tool or "").replace("/USDT", "")}'

                calcMesId = None
                if calc_.messages is not None:
                    calcMesId = calc_.messages.mesIds[chId_i]

                if calcMesId is not None:
                    tool = f'<a href="https://t.me/c/{str(chId).replace("-100", "")}/{calcMesId}">{tool}</a>'

                finished += f'{tool} {result}, '

            msg = f'⚡️<b>{"Текущие сделки" if lang == "ru" else "Current deals"}</b> ({getStrValueCount(in_deal_value_count, lang)}):'

            if msges.strip():
                msg += '\n\n' + msges.strip()

            if msg != '':
                msg += '\n\n<b>'
                msg += 'За день' if lang == 'ru' else 'Today'
                msg += ':</b> '

                msg += f'{getStrValueCount(live.todayValueCount, lang)}'

                current_date = get_str_by_datetime(
                    get_datetime_now(), "day.month"
                )

                msg += '\n<b>'
                msg += months[lang][int(current_date.split('.')
                                        [1]) - 1].capitalize()
                msg += ':</b> '

                tp_sl_show = 'к капиталу' if lang == 'ru' else 'to the capital'
                msg += f'{"+" if live.monthValueCount > 0 else ""}{get_print_float(live.monthValueCount, 1)}% {tp_sl_show}'

            if finished != '':
                msg += f'\n\n<b>Завершено:</b>\n' if lang == 'ru' else f'\n\n<b>Closed:</b>\n'
                msg += finished.strip()[:-1]

            if len(live.wait) > 0:
                msg += '\n\n<b>'
                msg += 'В ожидании: ' if lang == 'ru' else 'In wait: '
                msg += '</b>'
                for i, el in enumerate(live.wait):
                    tool = el.tool.replace('/USDT', '')
                    if el.messages is not None:
                        tool = f'<a href="https://t.me/c/{str(chId).replace("-100", "")}/{el.messages.mesIds[chId_i]}">{tool}</a>'

                    msg += tool
                    if i != len(live.wait) - 1:
                        msg += ', '

            if len(live.canceled) > 0:
                msg += '\n<b>'
                msg += 'Отменены: ' if lang == 'ru' else 'Canceled: '
                msg += '</b>'
                for i, el in enumerate(live.canceled):
                    tool = el.tool.replace('/USDT', '')
                    if el.messages is not None:
                        tool = f'<a href="https://t.me/c/{str(chId).replace("-100", "")}/{el.messages.mesIds[chId_i]}">{tool}</a>'

                    msg += tool
                    if i != len(live.canceled) - 1:
                        msg += ', '

            msg += '\n'

            week = channel_calc.getWeekStat()
            if week is not None:
                text = 'Статистика' if lang == 'ru' else 'Stats'
                msg += f'\n<a href="https://t.me/{RESULTS_CHANNEL_NAME}">{text}</a>'

            msg += '\n'
            msg += 'Сайт' if lang == 'ru' else 'Site'
            msg += ': proriski.com'

            try:
                if live.isNewMes or mesIds is None:
                    new_mes = await antiflood(
                        self.bot.send_message,
                        chId, msg,
                    )

                    new_live_mes_ids.append(str(new_mes.id))

                    if mesIds is not None:
                        await self.bot.unpin_chat_message(
                            int(chId), int(mesIds[chId_i])
                        )

                    await self.bot.pin_chat_message(
                        chId, new_mes.id
                    )
                else:
                    await antiflood(
                        self.bot.edit_message_text,
                        msg, chId, int(mesIds[chId_i])
                    )
            except Exception as e:
                logger.error(f'LIVE SEND ERROR: {e}')

        if len(new_live_mes_ids) == len(chIds):
            channel_calc.updateLiveInfo(
                SentMessages(
                    chIds=chIds,
                    mesIds=new_live_mes_ids,
                    langs=langs
                )
            )

    async def send_stats(self, calcId: int | None = None, is_active=False):
        texts = {
            'ru': {
                'title': '⚡️ <b>Результаты на эту неделю</b>',

                'title2': '⚡️ Результаты',
                'from': 'с',
                'to': 'по',

                'canceled': 'Отменённые',

                'prices': 'Купил/Продал',
                'result': 'Итого за неделю',
                'long': 'Лонг',
                'short': 'Шорт',
                'success': 'Процент успешных сделок',
            },
            'en': {
                'title': '⚡️ <b>Results for this week</b>',

                'title2': '⚡️ Results',
                'from': 'from',
                'to': 'to',

                'canceled': 'Cancelled',

                'prices': 'Bought/Sold',
                'result': 'Total for the week',
                'long': 'Long',
                'short': 'Short',
                'success': 'Success deals percent',
            },
        }

        if not is_active:
            lang = 'ru'
            data = channel_calc.getWeekStat(calcId)
            if data is None:
                msg = texts[lang]["title"]

                mes = await self.bot.send_message(
                    RESULTS_CHANNEL_ID, msg,
                )

                channel_calc.createWeekStat(
                    [RESULTS_CHANNEL_ID], [mes.id], [lang]
                )

        if not is_active:
            data = channel_calc.getWeekStat(calcId)
            if data is None:
                return
        else:
            data = channel_calc.getActiveStats(calcId or 0)
            if data is None:
                return

        ch_mes = data.get('messages', {})
        chIds: list[str] = ch_mes.get('chIds', []) if not is_active else [
            str(TOURNAMENT_CHANNEL_ID)]
        mesIds: list[str] = ch_mes.get(
            'mesIds', []) if not is_active else [str(1231)]
        langs: list[Literal['ru', 'en']] = ch_mes.get(
            'langs', []) if not is_active else ['ru']

        marathon_data: list[float | None] = data.get('marathon')
        marathon = ''

        if False and marathon_data is not None and len(marathon_data) > 0:
            week_num = 0
            week_value = 0

            marathon = '<b>Марафон 30 дней:</b>'
            for i, el in enumerate(marathon_data):
                if len(marathon_data) - week_num * 7 >= 7:
                    week_value += (el or 0)

                    if i + 1 == (week_num + 1) * 7:
                        week_num += 1
                        marathon += f'\n{week_num} неделя - '

                        if week_value is None:
                            marathon += 'нет сделок'
                        else:
                            marathon += getStrValueCount(week_value)
                        week_value = 0
                    continue

                marathon += f'\n{i + 1} день - '
                if el is None:
                    marathon += 'нет сделок'
                else:
                    marathon += getStrValueCount(el)

        for chId_i, chId in enumerate(chIds):
            lang = langs[chId_i]

            values: list[dict] = data.get('values')

            if not is_active:
                startDate = data.get('startDate')
                endDate = data.get('endDate')

                msg = f"<b>{texts[lang]['title2']} {texts[lang]['from']} {startDate} {texts[lang]['to']} {endDate}</b>"
            else:
                msg = 'Статистика трейдера'

            all_tp_count = 0
            all_sl_count = 0

            long_count = 0
            short_count = 0

            all_success_count = 0
            all_fail_count = 0

            tool_counts: dict[str, int] = {}

            msg_in_deal = ''
            msg_dates = ''

            for valueDate in values:
                date_msg = ''

                tp_count = 0
                sl_count = 0

                success_count = 0
                fail_count = 0

                canceled = ''

                num = 0
                for value in valueDate.get('calcs', []):
                    status: CALC_STATUS_TYPE = value.get('status', 'WAIT')
                    if status == 'WAIT':
                        continue

                    valueCount = value.get('valueCount')
                    openPrice = value.get('openPrice')
                    closePrice = value.get('closePrice')

                    calc_messages = value.get('messages')

                    tp_sl = ''
                    if valueCount is None:
                        tp_sl = transl_status(status, lang)
                    else:
                        tp_sl = getStrValueCount(valueCount, lang)

                        if valueCount == 0:
                            tp_count += 1
                            sl_count += 1
                        elif valueCount > 0:
                            tp_count += valueCount
                            success_count += 1

                            if closePrice > openPrice:
                                long_count += 1
                            else:
                                short_count += 1
                        else:
                            sl_count += abs(valueCount)
                            fail_count += 1

                            if closePrice > openPrice:
                                short_count += 1
                            else:
                                long_count += 1

                    link_start = ''
                    link_end = ''

                    if calc_messages:
                        calc_chId = calc_messages.get('chIds', [None])[0]
                        calc_mesId = calc_messages.get('mesIds', [None])[0]
                        link_start = f'<a href="https://t.me/c/{calc_chId.replace("-100", "")}/{calc_mesId}">' if calc_mesId is not None else ''
                        link_end = '</a>' if calc_mesId is not None else ''

                    tool = value.get("tool")
                    tool_num = ''
                    if tool not in tool_counts:
                        tool_counts[tool] = 1
                    else:
                        tool_counts[tool] += 1
                        tool_num = f'({tool_counts[tool]})'

                    if status == 'DEAL':
                        msg_in_deal += f'\n{link_start}<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b>{link_end}'
                    elif status == 'CANCEL':
                        if canceled != '':
                            canceled += ', '
                        canceled += f'{link_start}<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b>{link_end}'
                    else:
                        num += 1
                        date_msg += f'\n{num}. {link_start}<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b>{link_end} - {tp_sl}'

                tp_sl_result = round(tp_count - sl_count, 1)
                tp_sl_msg = ''
                if tp_count != 0 or sl_count != 0:
                    tp_sl_msg = f' ({getStrValueCount(tp_sl_result, lang)})'

                if date_msg.lstrip() != '' or canceled != '':
                    msg_dates += f'\n\n<b><u>{valueDate.get("date")}</u></b>{tp_sl_msg}'
                    msg_dates += f'{date_msg}'

                    if canceled != '':
                        msg_dates += f'\n\n{texts[lang]["canceled"]}: {canceled}'

                    # if success_count != 0 or fail_count != 0:
                    #     msg_dates += f'\n\n<b>{texts[lang]["success"]}</b>: {round((success_count * 100) / (success_count + fail_count))} %'

                all_success_count += success_count
                all_fail_count += fail_count
                all_tp_count += tp_count
                all_sl_count += sl_count

            if msg_in_deal != '':
                msg += '\n\n'
                msg += '<b>В сделке:</b>' if lang == 'ru' else '<b>In deal:</b>'
                msg += msg_in_deal
            msg += msg_dates
            msg += f'\n_________________________________'

            tp_sl_result = round(all_tp_count - all_sl_count, 1)

            if all_tp_count == 0 and all_sl_count == 0:
                if lang == 'ru':
                    msg += f'\n\nОжидаются ближайшие сделки'
                else:
                    msg += f'\n\nUpcoming deals are expected'

            if all_tp_count != 0 or all_sl_count != 0:
                msg += f'\n\n<b>{texts[lang]["result"]}</b>: '
                msg += f'{getStrValueCount(tp_sl_result, lang)}'
                msg += '\n'

            if long_count != 0 or short_count != 0:
                if long_count != 0:
                    msg += f'<b>{texts[lang]["long"]}</b>: {long_count}'
                if long_count != 0 and short_count != 0:
                    msg += ' / '
                if short_count != 0:
                    msg += f'<b>{texts[lang]["short"]}</b>: {short_count}'

            if all_success_count != 0 or all_fail_count != 0:
                msg += f'\n<b>{texts[lang]["success"]}</b>: {round((all_success_count * 100) / (all_success_count + all_fail_count))} %'

            try:
                await antiflood(
                    self.bot.edit_message_text,
                    msg + f'\n\n{marathon}', chId, mesIds[chId_i],
                )
            except Exception as e:
                logger.error(f'STATS SEND ERROR: {e}')

    async def send_vote(self, stat_id: int):
        stat = calculation.get(userId=1, calcId=stat_id)
        if stat is None:
            return

        rand = randint(1, 3)
        for i, CHANNEL_ID in enumerate(self.channels):
            lang = 'ru' if i == 0 else 'en'

            if rand == 1:
                q = f'👆 {stat.tool or "" or (stat.forexInfo.pair if stat.forexInfo is not None else "")}'

                if lang == 'ru':
                    ans = ['В рост', 'На падение']
                else:
                    ans = ['Long', 'Short']
            elif rand == 2:
                if lang == 'ru':
                    q = '👆 Войдете в сделку?'
                    ans = ['Да', 'Нет', 'Подумаю']
                else:
                    q = '👆 Will be in deal?'
                    ans = ['Yes', 'No', 'Thinking']
            else:
                if lang == 'ru':
                    q = '👆 Нравится график?'
                    ans = ['Да', 'Нет']
                else:
                    q = '👆 Do you like grafic?'
                    ans = ['Yes', 'No']

            await self.bot.send_poll(
                CHANNEL_ID, q, [InputPollOption(el) for el in ans], True
            )

        if stat_id in self.loading_vote_message_ids:
            cur_chat_id, cur_mes_id = self.loading_vote_message_ids[stat_id]
            await self.main_bot.edit_message_text(
                '✅ Опрос отправлен', cur_chat_id, cur_mes_id
            )
            self.loading_vote_message_ids.pop(stat_id)
