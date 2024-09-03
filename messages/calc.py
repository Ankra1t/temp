from datetime import datetime, timedelta
from typing import Literal
import requests
from telebot.async_telebot import AsyncTeleBot

from common.dt import get_datetime_now, get_str_by_datetime
from common.utils import get_decimal_count, get_lang, get_print_float
from messages.common import ENTER, TAB, transl_market, transl_status, transl_tr_style, transl_tr_type
from models import LANGUAGES_TYPE, TRADING_TYPE, Calculation, ForexInfo, TickerInfo

from Classes import calcService


months = {'ru': [
    'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
    'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
], 'en': [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]}


async def msg_calculate(bot: AsyncTeleBot, user_id: int, chat_id: int, is_try=False):
    lang = get_lang(user_id)  # TODO - delete

    data = bot.retrieve_data(user_id, chat_id) or {}
    updated_risk = data.get('updated_risk') or 1.
    type = data.get('calc_type', '')
    ticker = data.get('ticker')
    open_price = data.get('open_price')
    forex: ForexInfo | None = data.get('forex')
    tool: str = data.get('tool') or ''
    deposit: float | None = data.get('deposit')
    risk: tuple[float, bool] | None = data.get('risk')
    currency: str | None = data.get('currency')
    trading_type: TRADING_TYPE = data.get('trading_type', 'margin')

    risk_value = risk[0] if (risk is not None) else None
    if (risk is not None) and risk[1] and (deposit is not None):
        risk_value = risk[0] * deposit * 0.01 * updated_risk

    type_list = ['ticker', 'dep', 'risk', 'open']
    vars_dict = {
        'ticker': ticker,
        'dep': deposit,
        'risk': risk_value,
        'open': open_price,
    }

    point = {
        'ru': {
            'ticker': 'Тикер',
            'dep': 'Депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена входа',
            'pair': 'Валютная пара',

            'trading_type': 'Тип торговли',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Deposit',
            'risk': 'Deal risk',
            'open': 'Open price',
            'pair': 'Currency pair',

            'trading_type': 'Trading type',
        },
        'uz': {
            'ticker': 'Ticker',
            'dep': 'Depozit',
            'risk': 'Risk',
            'open': 'Narxi',
            'pair': 'Valyuta juftligi',

            'trading_type': 'Savdo turi',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Depozito',
            'risk': 'Risk',
            'open': 'Fiyat',
            'pair': 'Para çifti',

            'trading_type': 'Ticaret türü',
        },
    }

    pair = '/'.join(forex.pair) if (forex is not None) else ''
    text = ''

    if type == 'forex' and pair != '':
        text += f'<b><u>{pair}</u></b>'
    elif type == 'crypto' and tool != '':
        text += f'<b><u>{tool}</u></b>'
    text += f' - {transl_market(type, lang)} {"(demo)" if is_try else ""}\n\n'

    for el in type_list:
        item = vars_dict[el]
        if item is not None:
            if item == 'ticker':
                text += f'<b>{point[lang][el]}</b>: {item}\n'
            else:
                text += ''.join((
                    f'<b>{point[lang][el]}</b>: ',
                    f'{item} ',
                    (currency or '') if (
                        type != 'forex' or forex is None) else forex.pair[1],
                    '\n'
                ))

    if not is_try:
        text += f'\n<b>{point[lang]["trading_type"]}</b>: {transl_tr_type(trading_type, lang)}\n'

    text += '\n'
    return text


def msg_calculation(lang: LANGUAGES_TYPE, calc: Calculation, is_try=False):
    is_saved = calc.inStat
    calc_result = calcService.get_result(calc)

    if calc.openPrice > calc.stopLoss:
        long_short = 'long'
    else:
        long_short = 'short'

    texts = {
        'ru': {
            'dep': 'Депозит' if not is_saved else 'Итоговый депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена',
            'stop': 'Стоп',

            'conclusion': 'Тейк-профит',

            'profit': 'Прибыль' if not is_saved else 'Прибыль от сделки',
            'buy': 'Купите' if not is_saved else 'Купили',
            'sell': 'Продайте' if not is_saved else 'Продали',

            'sum': 'Сумма покупки' if long_short == 'long' else 'Сумма продажи',
            'style': 'Стиль торговли',
            'trading_type': 'Тип торговли',

            'coin': 'монет',
            'paper': 'акций',
            'lot': 'лота',

            'sl': 'стоп лосс',
            'breakeven': 'безубыток',

            'to': 'к',

            'fee': 'Комиссия биржи',
            'risk_percent': 'Риск в процентах',

            'description': 'Описание',
            'comment': 'Комментарий',
        },
        'en': {
            'dep': 'Deposit' if not is_saved else 'Final deposit',
            'risk': 'Deal risk',
            'open': 'Price',
            'stop': 'Stop loss',

            'conclusion': 'Take profit',

            'profit': 'Profit' if not is_saved else 'Deal profit',
            'buy': 'Buy' if not is_saved else 'Bought',
            'sell': 'Sell' if not is_saved else 'Sold',

            'sum': 'Sum',
            'style': 'Trading style',
            'trading_type': 'Trading type',

            'coin': 'coins',
            'paper': 'shares',
            'lot': 'lots',

            'sl': 'stop loss',
            'breakeven': 'breakeven',

            'to': 'to',

            'fee': 'Exchange fee',
            'risk_percent': 'Risk in percent',

            'description': 'Description',
            'comment': 'Сomment',
        },
        'uz': {
            'dep': 'Depozit' if not is_saved else 'Yakuniy depozit',
            'risk': 'Risk',
            'open': 'Narxi',
            'stop': 'Stop loss',

            'conclusion': 'Foyda oling',

            'profit': 'Profit' if not is_saved else 'Bitim profit',
            'buy': 'Sotib oling' if not is_saved else 'Sotib oling',
            'sell': 'Sotmoq' if not is_saved else 'Sotilgan',

            'sum': 'So\'m',
            'style': 'Savdo uslubi',
            'trading_type': 'Savdo turi',

            'coin': 'tangalar',
            'paper': 'ulushlar',
            'lot': 'juda ko\'p',

            'sl': "Yo'qotishni to'xtating",
            'breakeven': 'beziyon',

            'to': 'ga',

            'fee': 'BIRJA BERISH',
            'risk_percent': 'Xavf foiz',

            'description': 'Tavsif',
            'comment': 'Sanktsiya',
        },
        'tr': {
            'dep': 'Depozito' if not is_saved else 'Son depozito',
            'risk': 'Risk',
            'open': 'Fiyat',
            'stop': 'Stop loss',

            'conclusion': 'Take profit',

            'profit': 'Kâr' if not is_saved else 'Anlaşmak Kâr',
            'buy': 'Satın almak' if not is_saved else 'Satın alınmış',
            'sell': 'Satmak' if not is_saved else 'Satılmış',

            'sum': 'Meblağ',
            'style': 'Ticaret tarzı',
            'trading_type': 'Ticaret türü',

            'coin': 'madeni para',
            'paper': 'hisse senetleri',
            'lot': 'çok',

            'sl': 'durdurma kaybı',
            'breakeven': 'başa baş',

            'to': 'ile',

            'fee': 'Borsa ücreti',
            'risk_percent': 'Yüzde risk',

            'description': 'Tanım',
            'comment': 'Comment',
        },
    }

    attention = ''
    count_zero = 0
    for el in calc_result.tp_values:
        if el == 0:
            count_zero += 1

    if count_zero > calc_result.tp_count // 2:
        attention = '\n⚠️ При текущих значениях стоп-лосса и цены входа, тейк‑профит равен нулю, что делает сделку некорректной.'
        attention += '\n<b>Рекомендуем</b> изменить цену входа или стоп-лосс\n'

    if calc.market == 'crypto':
        tool_name = texts[lang]["coin"]
    elif calc.market == 'forex':
        tool_name = texts[lang]["lot"]
    else:
        tool_name = texts[lang]["paper"]

    # Валюта торговли
    trading_currency = calc.currency
    tool = calc.tool or ''
    if calc.forexInfo is not None and calc.market == 'forex':
        trading_currency = calc.forexInfo.pair[1]
        tool = ''.join(calc.forexInfo.pair)

    trading_style_type = ''
    if not is_try:
        t_style = transl_tr_style(calc.tradingStyle, lang)
        if t_style is not None:
            trading_style_type += f'<b>{texts[lang]["style"]}</b>: {t_style}'

            if calc.tradingType:
                trading_style_type = f' ({transl_tr_type(calc.tradingType, lang)})'
            trading_style_type += '\n'

    # Округление
    round_count = calc.roundCount or 5
    price_round_count = max(
        get_decimal_count(calc.openPrice),
        get_decimal_count(calc.stopLoss),
        round_count
    )

    # Кол-во и сумма покупки
    count_bet, value_bet = calc_result.count_bet, calc_result.value_bet

    fee_text = ''
    if calc_result.fee is not None:
        fee_text = f'<b>{texts[lang]["fee"]}</b>: {get_print_float(calc_result.fee, round_count)} {calc.currency}\n'

    if is_saved:
        profit = calc.profit or 0.
        profit_result = f"""<b>{texts[lang]['profit']}: </b>{get_print_float(profit, round_count)} {calc.currency}"""
    else:
        saved_mes = ''

        p_show = ''
        conclusion = ''
        for i in range(calc_result.tp_count):
            tp_ratio = calc.tpRatio[i]
            tp_val = calc_result.tp_values[i]
            p_val = calc_result.profit_values[i]

            if tp_val == 0:
                if lang == 'ru':
                    conclusion += f'Тейк-профит ({tp_ratio} {texts[lang]["to"]} 1) не может быть рассчитан'
                elif lang == 'uz':
                    conclusion += f'Foyda oling ({tp_ratio} {texts[lang]["to"]} 1) hisoblab bo\'lmaydi'
                elif lang == 'tr':
                    conclusion += f'Fayda ({tp_ratio} {texts[lang]["to"]} 1) sayılmaz'
                elif lang == 'en':
                    conclusion += f'Take profit ({tp_ratio} {texts[lang]["to"]} 1) cannot be calculated'
            else:
                conclusion += f' <code>{get_print_float(tp_val, price_round_count)}</code> {trading_currency}'
                conclusion += f' | {get_print_float(p_val, round_count if p_val < 10 else 1)} {calc.currency} ({tp_ratio} {texts[lang]["to"]} 1)'

                if calc_result.profit_rate_values is not None:
                    rate = calc_result.profit_rate_values[i]
                    conclusion += f' -- (<b>{get_print_float(count_bet * rate, 2)} {tool_name}</b>) {get_print_float(rate * 100, round_count)}%'

            if i != calc_result.tp_count - 1:
                conclusion += '\n'

        profit_result = f"""<b>{texts[lang]['conclusion']} | {texts[lang]["profit"]}</b>:
{conclusion}"""

    demo_show = ''
    if is_try:
        demo_show = ' - demo'

    if calc.status != 'FINISH':
        status = f'{transl_status(calc.status, lang)}'
    else:
        tp_sl_count = (calc.profit or 0) / calc.riskValue

        if tp_sl_count == 0:
            status = f'{texts[lang]["breakeven"]}'
        elif tp_sl_count > 0:
            status = f'{get_print_float(tp_sl_count, 1)} {texts[lang]["to"]} 1'
        else:
            status = f'{(get_print_float(tp_sl_count, 1) + " ") if tp_sl_count != 1 else ""}{texts[lang]["sl"]}'

    decription = ''
    if calc.description is not None:
        decription = f'<b>{texts[lang]["description"]}</b>: {calc.description}\n'

    comment = ''
    if calc.comment is not None:
        comment = f'<b>{texts[lang]["comment"]}</b>: {calc.comment}\n'

    return '\n'.join((
        f'#<b><u>{tool.replace("/USDT", "").upper()}</u></b>{demo_show} | {status}',
        attention,
        f'<b>{texts[lang]["buy" if long_short == "long" else "sell"]}</b>: <code>{get_print_float(count_bet, 0 if count_bet > 10 else 2)}</code> {tool_name}',
        f'<b>{texts[lang]["sum"]}</b>: {get_print_float(value_bet, price_round_count if value_bet < 10 else 1)} {calc.currency}',
        f'<b>{texts[lang]["open"]}</b>: <code>{get_print_float(calc.openPrice, price_round_count)}</code> {trading_currency}',
        f'<b>{texts[lang]["stop"]}</b>: <code>{get_print_float(calc.stopLoss, price_round_count)}</code> {trading_currency}',
        '',
        profit_result,
        '',
        f'<b>{texts[lang]["dep"]}</b>: {get_print_float(calc.deposit + (calc.profit or 0.))} {calc.currency}',
        f"""<b>{texts[lang]["risk"]}</b>: {get_print_float(calc.riskValue)} {calc.currency} {f"{ENTER}<b>{texts[lang]['risk_percent']}</b>: {get_print_float(calc.riskValue / calc.deposit * 100, 1)}%" if is_try else ""}""",
        fee_text + trading_style_type,
        decription + comment
    ))


def msg_channel_calculation(
    calc: Calculation,
    lang: Literal['ru', 'en'] = 'ru',
    without_stop=False,
    time: str = '',
    count=-1,
    tickerInfo: TickerInfo | None = None,
    description: str | None = None,
    week_stat_link: str | None = None,
    date: str | None = None,
    try_link: str = '',
):
    description = description if lang == 'ru' else None

    monthCount = tickerInfo.monthCount if tickerInfo is not None else 0
    status = calc.status

    if calc.profit is not None or status == 'FINISH':
        return msg_channel_calc_result(
            calc, lang, time, count, description, week_stat_link, date, try_link
        )

    calc_result = calcService.get_result(calc)

    texts = {
        'ru': {
            'open': 'Войду по' if status == 'WAIT' else 'Вошел по' if status == 'DEAL' else 'Вход',

            'price': 'Цена сейчас',
            'now': 'Сейчас',

            'stop': 'Стоп',
            'take': 'Тейк',
            'style': '<b>С</b>тиль',

            'tp': 'тейка',
            'sl': 'стопа',

            'direct': 'Направление',
            'to': 'к',

            'deal': '<b>С</b>делка',
            'avg': 'среднесрочный',
            'day': 'внутри дня',

            'buy/sell': '<b>П</b>окупают/продают',
            'change24': '<b>И</b>зменение за 24ч',
            'turnover24': '<b>О</b>борот за 24ч',

            'DEAL': 'В сделке',
            'CANCEL': 'Отменён',
            'WAIT': 'В ожидании',
            'try': 'Рассчитать',
            'chart': 'График',
        },
        'en': {
            'open': 'Will enter by' if status == 'WAIT' else 'Entered by' if status == 'DEAL' else 'Enter',

            'stop': 'Stop',
            'price': 'Current price',
            'now': 'Now',

            'take': 'Take',
            'style': '<b>S</b>tyle',

            'tp': 'тейка',
            'sl': 'стопа',

            'direct': 'Direction',
            'to': 'to',

            'deal': '<b>T</b>rade',
            'avg': 'medium-term',
            'day': 'intraday',

            'buy/sell': '<b>B</b>uy/sell',
            'change24': '<b>C</b>hange in 24h',
            'turnover24': '<b>T</b>urnover in 24h',

            'DEAL': 'In deal',
            'CANCEL': 'Cancel',
            'WAIT': 'Waiting',
            'try': 'Calculate',
            'chart': 'Chart',
        }
    }

    # Валюта торговли
    trading_currency = calc.currency
    tool = calc.tool or ''
    if calc.forexInfo is not None and calc.market == 'forex':
        trading_currency = calc.forexInfo.pair[1]
        tool = ''.join(calc.forexInfo.pair)

    if trading_currency == 'USDT' or trading_currency == 'USD':
        trading_currency = '$'
    else:
        trading_currency = f' {trading_currency}'

    t_style = transl_tr_style(calc.tradingStyle, lang)
    trading_style_type = ''
    if t_style is not None:
        trading_style_type += f'\n\n{t_style.capitalize()}'
        if time != '':
            trading_style_type += f' ({texts[lang][time]})'

    # Округление
    round_count = calc.roundCount or 5
    price_round_count = max(
        get_decimal_count(calc.openPrice),
        get_decimal_count(calc.stopLoss),
        round_count
    )

    diffOpSl = calc.openPrice - calc.stopLoss
    current_value_count = None
    current_values_sum = None
    if tickerInfo and tickerInfo.indexPrice and status == 'DEAL':
        current_value_count = get_print_float(
            (tickerInfo.indexPrice - calc.openPrice) / diffOpSl, 1
        )
        current_values_sum = get_print_float(
            calc.riskValue * float(current_value_count), 1)

    profit_result = ''
    if not without_stop:
        for i in range(calc_result.tp_count):
            tp_ratio = calc.tpRatio[i]
            tp_val = calc_result.tp_values[i]

            if (
                (status == 'CANCEL' and i == 0) or
                (
                    tickerInfo and tickerInfo.indexPrice and
                    (
                    (diffOpSl > 0 and tickerInfo.indexPrice > tp_val) or
                    (diffOpSl < 0 and tickerInfo.indexPrice < tp_val)
                    )
                ) or i == 0
            ):
                profit_result = f'\n<b>{texts[lang]["take"]}</b> ({get_print_float(calc.riskValue * tp_ratio, 2)}{trading_currency}): '
                profit_result += f'<code>{get_print_float(tp_val, price_round_count)}</code>{trading_currency}'

    count_show = ''
    if count != -1:
        count_show = f'{count}. '

    price_show = ''
    if tickerInfo and tickerInfo.indexPrice is not None:
        price_show = f'<code>{get_print_float(tickerInfo.indexPrice, 0 if tickerInfo.indexPrice > 100 else 4)}</code>{trading_currency}'

    def link(value: str):
        return f'<a href="https://t.me/trade_res">{value}</a>'

    current_date = get_str_by_datetime(get_datetime_now(), "day.month")
    month = ('За' if lang == 'ru' else 'For') + ' ' + \
        months[lang][int(current_date.split('.')[1]) - 1]

    chart_link = ''
    if try_link != '':
        chart_link = f'https://ru.tradingview.com/chart/?symbol=BYBIT%3A{(calc.tool or "").replace("/", "")}.P'
        res = requests.get(chart_link)

        if res.status_code >= 200 and res.status_code < 300:
            chart_link = f' | <a href="{chart_link}">{texts[lang]["chart"]}</a>'
        else:
            chart_link = ''

    return '\n'.join((
        f'{count_show}<b>{link(tool.replace("/USDT", "").upper())}</b>{f" - {price_show}" if (status == "WAIT" and price_show != "") else ""} | {texts[lang][status]}',
        '',
        f'<b>{texts[lang]["open"]}</b>: <code>{get_print_float(calc.openPrice, price_round_count)}</code>{trading_currency}',
    )) \
        + (
            (
                f'\n<b>{texts[lang]["price"]}</b>: {price_show}'
            ) if status == 'DEAL' else ''
    ) \
        + (
            (
                f'\n<b>{texts[lang]["stop"]}</b> ({get_print_float(calc.riskValue, 2)}{trading_currency}): <code>{get_print_float(calc.stopLoss, price_round_count)}</code>{trading_currency}'
                + profit_result
            ) if not without_stop else ''
    ) \
        + (f'\n\n⚡️ <b>{texts[lang]["now"]}</b>: {"+" if float(current_value_count) > 0 else ""}{current_value_count} {texts[lang]["tp" if float(current_value_count) >= 0 else "sl"]} ({current_values_sum}{trading_currency})' if current_value_count is not None else '') \
        + (f'\n\n{description}' if description else '') \
        + (f'\n\n{calc.comment.strip()}' if (calc.comment and lang == 'ru') else '') \
        + (
            (
                f'\n\n<b>{month}:</b> '
                f"{f'торгую {monthCount} раз(а)' if lang == 'ru' else f'traded {monthCount} time(s)'}"
                f'\n<b>{"Результат" if lang == "ru" else "Results"}</b>: {"+" if tickerInfo.monthValue > 0 else ""}{get_print_float(tickerInfo.monthValue, 1)} '
                f'{("тейков" if lang == "ru" else "take") if tickerInfo.monthValue > 0 else ("стопов" if lang == "ru" else "stop") }'
            ) if status == 'WAIT' and tickerInfo else "") \
        + trading_style_type \
        + (f'\n\n<a href="{try_link}">{texts[lang]["try"]}</a>{chart_link}\n' if try_link != '' else '')


def msg_channel_calc_result(
    calc: Calculation,
    lang: LANGUAGES_TYPE,
    time='',
    count=-1,
    description: str | None = None,
    week_stat_link: str | None = None,
    date: str | None = None,
    try_link='',
):
    if calc.profit is None:
        return ''

    calc_result = calcService.get_result(calc)

    texts = {
        'ru': {
            'open': '<b>Входил по</b>',
            'close': '<b>Закрыл по</b>',
            'result': '<b>Результат</b>',

            'stop': '<b>Стоп</b>',
            'take': '<b>Тейк</b>',
            'tp': 'тейка',
            'sl': 'стопа',

            'style': '<b>С</b>тиль торговли',
            'deal': '<b>С</b>делка',

            'to': 'к',

            'avg': 'среднесрочный',
            'day': 'внутри дня',

            'short': 'шорт',
            'long': 'лонг',

            'date': 'Дата',
            'try': 'Рассчитать',

            'breakeven': 'безубыток',
            'chart': 'График',
        },
        'en': {
            'open': '<b>Entered by</b>',
            'close': '<b>Closed</b>',
            'result': '<b>Result</b>',

            'stop': '<b>Stop</b>',
            'take': '<b>Take</b>',
            'tp': 'take',
            'sl': 'stop',

            'style': '<b>T</b>rading style',
            'deal': '<b>T</b>rade',

            'to': 'to',

            'avg': 'medium-term',
            'day': 'intraday',

            'short': 'short',
            'long': 'long',

            'date': 'Date',
            'try': 'Calculate',

            'breakeven': 'breakeven',
            'chart': 'Chart',
        }
    }

    # Валюта торговли
    trading_currency = calc.currency
    tool = calc.tool or ''
    if calc.forexInfo is not None and calc.market == 'forex':
        trading_currency = calc.forexInfo.pair[1]
        tool = ''.join(calc.forexInfo.pair)

    if trading_currency == 'USDT' or trading_currency == 'USD':
        trading_currency = '$'
    else:
        trading_currency = f' {trading_currency}'

    take_or_stop = 'take' if calc.profit > 0 else 'stop'

    tp_sl_count = (calc.profit / calc.riskValue)
    close_price = calc.openPrice + \
        (calc.openPrice - calc.stopLoss) * \
        tp_sl_count

    count_show = ''
    if count != -1:
        count_show = f'{count}. '

    if calc.profit == 0:
        result = f'{texts[lang]["breakeven"]}'
    elif take_or_stop == 'take':
        result = f'{get_print_float(tp_sl_count, 1)} {texts[lang]["to"]} 1'
    else:
        result = f'{(get_print_float(tp_sl_count, 1) + " ") if tp_sl_count != 1 else ""}{texts[lang]["sl"]}'

    nearTake = calc.tpRatio[0]
    nearValue = calc_result.tp_values[0]
    for i in range(len(calc_result.tp_values)):
        tp_ratio = calc.tpRatio[i]
        tp_val = calc_result.tp_values[i]

        if (abs(close_price - tp_val) < abs(close_price - nearValue)):
            nearValue = tp_val
            nearTake = tp_ratio

    trading_style_type = ''
    t_style = transl_tr_style(calc.tradingStyle, lang)
    if t_style is not None or time != '':
        trading_style_type += '\n\n'
    if t_style is not None:
        trading_style_type += f'{t_style.capitalize()}'
        if time != '':
            trading_style_type += f' ({texts[lang][time]})'

    def link(value: str):
        return f'<a href="https://t.me/trade_res">{value}</a>'

    chart_link = ''
    if try_link != '':
        chart_link = f'https://ru.tradingview.com/chart/?symbol=BYBIT%3A{(calc.tool or "").replace("/", "")}.P'
        res = requests.get(chart_link)

        if res.status_code >= 200 and res.status_code < 300:
            chart_link = f' | <a href="{chart_link}">{texts[lang]["chart"]}</a>'
        else:
            chart_link = ''

# <b>{texts[lang]["date"]}</b>: {date}
    return f"""{count_show}<b>{link(tool).replace('/USDT', '')}</b> | {'Завершено' if lang == 'ru' else 'Finished'}

{texts[lang]["open"]}: {get_print_float(calc.openPrice)}{trading_currency}
{texts[lang]["stop"]} ({get_print_float(calc.riskValue, 2)}{trading_currency}): {get_print_float(calc.stopLoss)}{trading_currency}
{texts[lang]["take"]} ({get_print_float(calc.riskValue * nearTake, 2)}{trading_currency}): {get_print_float(nearValue)}{trading_currency}

⚡️ {texts[lang]["close"]}: {get_print_float(close_price)}{trading_currency}
⚡️ {texts[lang]["result"]}: {result}""" \
        + (f'\n\n{description}' if description else '') \
        + trading_style_type \
        + (f'\n\n<a href="{try_link}">{texts[lang]["try"]}</a>{chart_link}\n' if try_link != '' else '')


def msg_calc_list(lang: LANGUAGES_TYPE, calcs: list[Calculation], type: str):
    texts = {
        'ru': {
            'deal': 'Список в сделке',
            'done': 'Список завершенных сделок',
            'canceled': 'Список отмененных сделок',
            'wait': 'Список ожидающих сделок',
            'info': 'Нажмите на номер для действий',
            'price': 'Вход/Стоп' if type != 'done' else 'Цена входа/закрытия',
            'result': 'Результат'
        },
        'en': {
            'deal': 'List in the transaction',
            'done': 'List of completed transactions',
            'canceled': 'List of canceled transactions',
            'wait': 'List of waiting transactions',
            'info': 'Click on the number to take action',
            'price': 'Open/Stop' if type != 'done' else 'Input/Closing price',
            'result': 'Result'
        },
        'uz': {
            'deal': 'Bitimdagi ro\'yxat',
            'done': 'To\'ldirilgan bitimlar ro\'yxati',
            'canceled': 'Bekor qilingan bitimlar ro\'yxati',
            'wait': 'Kutish bitimlarining ro\'yxati',
            'info': 'Harakatni olish uchun raqamni bosing',
            'price': 'Ochiq/To\'xtash' if type != 'done' else 'Kirish/yopilish narxi',
            'result': 'Natija'
        },
        'tr': {
            'deal': 'İşlemdeki liste',
            'done': 'Tamamlanan işlemlerin listesi',
            'canceled': 'İptal edilen işlemlerin listesi',
            'wait': 'Bekleme işlemlerinin listesi',
            'info': 'Harekete geçmek için numarayı tıklayın',
            'price': 'Aç/Stop' if type != 'done' else 'Giriş/Kapanış Fiyatı',
            'result': 'Sonuç'
        },
    }

    msg = texts[lang][type]

    if len(calcs) == 0:
        msg += '\n👉 Нет расчётов, требующих дествий'
        return msg

    tools = {}

    for el in calcs:
        tool = (el.tool or "").replace("/USDT", "")

        if tool in tools:
            tools[tool] += 1
        else:
            tools[tool] = 1

        count = ''
        if tools[tool] > 1:
            count = f'_{tools[tool]}'

        msg += f'\n\n/<b>{tool}{count}</b>'
        msg += f' ({(datetime.fromisoformat((el.createdAt or "").replace("Z", "")) + timedelta(hours=3)).strftime("%d.%m %H:%M")})'

        if type == 'done':
            tp_sl_count = ((el.profit or 0) / el.riskValue)
            close_price = el.openPrice + \
                (el.openPrice - el.stopLoss) * \
                tp_sl_count
            msg += f'\n{texts[lang]["price"]}: <b>{get_print_float(el.openPrice)} / {get_print_float(close_price)}</b>'
            msg += f'\n{texts[lang]["result"]}: <b>{get_print_float(el.profit or 0)} {el.currency}</b>'
        else:
            msg += f'\n{texts[lang]["price"]}: <b>{get_print_float(el.openPrice)} / {get_print_float(el.stopLoss)}</b>'

    return msg


def msg_calculate_delete(lang: LANGUAGES_TYPE, prev_message: str):
    texts = {
        'ru': 'Хотите удалить расчёт',
        'en': 'Do you want to delete the calculation',
        'uz': 'Hisoblashni o\'chirmoqchimisiz?',
        'tr': 'Hesaplamayı silmek istiyor musunuz',
    }

    return f"""{prev_message.strip()}

{TAB}<b>{texts[lang]}</b>?"""


def msg_calculate_change(lang: LANGUAGES_TYPE, prev_message: str):
    texts = {
        'ru': 'Что хотите изменить',
        'en': 'What do you want to change',
        'uz': 'Siz nimani o\'zgartirishni xohlaysiz',
        'tr': 'Neyi değiştirmek istiyorsun',
    }

    return f"""{prev_message.strip()}

{TAB}<b>{texts[lang]}?</b>"""


def msg_calculation_saved(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Расчет сохранен',
        'en': 'The calculation has been saved',
        'uz': 'Hisoblash saqlandi',
        'tr': 'Hesaplama kaydedildi',
    }

    return f'✅ {texts[lang]}!'


def msg_calculation_deleted(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Расчёт удалён',
        'en': 'Calcultaion deleted',
        'uz': 'Hisoblash o\'chirildi',
        'tr': 'Hesaplama silindi',
    }

    return f'⭕️ {texts[lang]}!'
