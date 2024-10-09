from datetime import datetime, timedelta
from typing import Literal, Optional
from common.utils import get_lang, get_print_float, getNounByNumber

from models import LANGUAGES_TYPE, CalcTrailingStop, Calculation
from db import db


def get_html_from_calc(user_id: int, calc: Calculation, saved=False):
    if calc.forexInfo is not None:
        return get_html_from_forex_calc(user_id, calc, saved)
    else:
        return get_html_from_crypto_calc(user_id, calc, saved)


def get_html_from_crypto_calc(
    user_id: int,
    calc: Calculation,
    saved=False,
):
    lang = get_lang(user_id)

    point = {
        'ru': {
            'dep': 'Депозит',
            'risk': 'Риск',
            'open': 'Цена',
            'sl': 'Стоп',
            'conclusion': 'Тейк-профит',
            'count': 'Кол-во',
            'sum': 'Сумма',
            'style': 'Стиль торговли',
            'profit': 'Прибыль',
            'coin': 'монет',
            'buy': 'Покупка',
            'sell': 'Продажа',
        },
        'en': {
            'dep': 'Deposit',
            'risk': 'Risk',
            'open': 'Price',
            'sl': 'Stop loss',
            'conclusion': 'Take profit',
            'count': 'Count',
            'sum': 'Sum',
            'style': 'Trading style',
            'profit': 'Profit',
            'coin': 'tokens',
            'buy': 'Buy',
            'sell': 'Sell',
        }
    }

    trading_style = (calc.tradingStyle or '').capitalize()

    # Округление
    round_count = calc.roundCount or 5

    # Кол-во покупки
    count_bet = (
        calc.riskValue /
        max(abs(calc.openPrice - calc.stopLoss), 0.00001)
    )

    # Сумма покупки
    value_bet = count_bet * calc.openPrice

    if saved:
        profit_info = get_html_from_calc_results(user_id, calc)
    else:
        p_show = ''
        conclusion = ''
        for i in range(len(calc.tpRatio)):
            tp_ratio_i = calc.tpRatio[i]
            tp_i = max(
                calc.openPrice +
                (calc.openPrice - calc.stopLoss) * tp_ratio_i,
                0
            )

            tp_class = 'tp_default'
            coins_show = ''
            percent_show = ''
            rate = 1
            if calc.splitValues is not None and len(calc.splitValues) != 0:
                percent = calc.splitValues[i]
                rate = percent / 100
                count = get_print_float(count_bet * rate, 2)

                tp_class = 'tp_item'
                percent_show = f'{get_print_float(percent, round_count)}%'
                coins_show = f'<b>{count} {point[lang]["coin"]}</b>'

            conclusion += f'<div class="{tp_class}">'
            conclusion += f'<div class="tp_val"><b>x{tp_ratio_i}</b> {percent_show}</div>'
            conclusion += f'<div class="tp_count"><u>{get_print_float(tp_i, round_count)} {calc.currency}</u> {coins_show}</div>'
            conclusion += f'</div>'

            p_show += f'<p class="value">{get_print_float(abs(calc.openPrice - tp_i) * rate * count_bet, round_count)}</p>'

        profit_info = f"""
            <div class="block">
                <p class="name">{point[lang]['conclusion']}</p>
                <div class="tp">
                    {conclusion}
                </div>
            </div>
            <div class="block">
                <p class="name">{point[lang]['profit']} (<b>{calc.currency}</b>)</p>
				<div class="profit">
                    {p_show}
                </div>
            </div>
        """

    tool = calc.tool or 'BTC/USDT'
    trading_type = 'buy' if calc.openPrice < calc.stopLoss else 'sell'
    saved = '' if not calc.inStat else """
<svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <rect width="20" height="20" rx="4" fill="#06BD32" />
    <path
        d="M8.33333 11.3333L13.25 6.41667C13.4028 6.26389 13.5972 6.1875 13.8333 6.1875C14.0694 6.1875 14.2639 6.26389 14.4167 6.41667C14.5694 6.56944 14.6458 6.76389 14.6458 7C14.6458 7.23611 14.5694 7.43056 14.4167 7.58333L8.91666 13.0833C8.75 13.25 8.55555 13.3333 8.33333 13.3333C8.11111 13.3333 7.91666 13.25 7.75 13.0833L5.58333 10.9167C5.43055 10.7639 5.35416 10.5694 5.35416 10.3333C5.35416 10.0972 5.43055 9.90278 5.58333 9.75C5.73611 9.59722 5.93055 9.52083 6.16666 9.52083C6.40278 9.52083 6.59722 9.59722 6.75 9.75L8.33333 11.3333Z"
        fill="white" />
</svg>"""

    return f"""
<header class="header">
    <div class="header_name">
        <div class="title">{tool}</div>
        <div class="{trading_type}">{point[lang][trading_type]}</div>
    </div>
    { saved }
</header>
<div class="row">
    <div class="block">
        <div class="value">{get_print_float(calc.riskValue)} {calc.currency}</div>
        <div class="name">{point[lang]['risk']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(calc.openPrice, round_count)} {calc.currency}</div>
        <div class="name">{point[lang]['open']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(calc.newStop or calc.stopLoss, round_count)} {calc.currency}</div>
        <div class="name">{point[lang]['sl']}</div>
    </div>
</div>
<div class="row">
    <div class="block">
        <div class="value">{get_print_float(count_bet)} {point[lang]["coin"]}</div>
        <div class="name">{point[lang]['count']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(value_bet)} {calc.currency}</div>
        <div class="name">{point[lang]['sum']}</div>
    </div>
</div>
{profit_info}
"""
    # <div class="point">
    #     <p class="name">{point[lang]['dep']}</p>
    #     <p class="value">{get_print_float(calc.deposit)} {calc.currency}</p>
    # </div>
    # '<div class="point">'
    #     f'<p class="name">{point[lang]["style"]}</p>'
    #     f'<p class="value">{trading_style}</p>'
    # '</div>'


def get_count_value_bet(calc: Calculation, lot=pow(10, 5)):
    """Возвращает кол-во и сумму покупки, коэффициент спота"""
    spot_rate = 1

    if calc.market == 'forex' and calc.forexInfo is not None:
        value_bet = (
            calc.riskValue / abs(calc.openPrice - calc.stopLoss)
        )
        count_bet = value_bet / lot

        if calc.currency == calc.forexInfo.pair[1]:
            value_bet *= calc.openPrice
        elif calc.currency == calc.forexInfo.pair[0]:
            count_bet *= calc.stopLoss
            value_bet = count_bet * lot
        else:
            BASExxx = f'{calc.currency}/{calc.forexInfo.pair[1]}'
            yyyBASE = f'{calc.forexInfo.pair[0]}/{calc.currency}'
            count_bet *= calc.forexInfo.cross_prices.get(BASExxx, 1)
            value_bet = count_bet * lot * \
                calc.forexInfo.cross_prices.get(yyyBASE, 1)
    else:
        count_bet = calc.riskValue / abs(calc.openPrice - calc.stopLoss)
        value_bet = count_bet * calc.openPrice

    if calc.tradingType == 'spot' and value_bet > calc.deposit:
        spot_rate = calc.deposit / value_bet

        count_bet *= spot_rate
        value_bet = calc.deposit

    return count_bet, value_bet, spot_rate


def get_html_from_forex_calc(
    user_id: int,
    calc: Calculation,
    saved=False,
):
    if calc.forexInfo is None:
        return 'Ошибка'

    lang = get_lang(user_id)
    point = {
        'ru': {
            'dep': 'Депозит',
            'risk': 'Риск',
            'open': 'Цена',
            'sl': 'Стоп',
            'conclusion': 'Тейк-профит',
            'count': 'Кол-во',
            'sum': 'Сумма',
            'style': 'Стиль торговли',
            'profit': 'Прибыль',
            'lot': 'лота',
            'buy': 'Покупка',
            'sell': 'Продажа',
        },
        'en': {
            'dep': 'Deposit',
            'risk': 'Risk',
            'open': 'Price',
            'sl': 'Stop loss',
            'conclusion': 'Take profit',
            'count': 'Count',
            'sum': 'Sum',
            'style': 'Trading style',
            'profit': 'Profit',
            'lot': 'lots',
            'buy': 'Buy',
            'sell': 'Sell',
        }
    }

    pair = '/'.join(calc.forexInfo.pair)
    LOT = pow(10, 5)

    trading_style = (calc.tradingStyle or '').capitalize()

    # Валюта торговли
    trading_currency = calc.forexInfo.pair[1]

    # Округление
    round_count = calc.roundCount or 5

    # Сумма покупки
    value_bet = (
        calc.riskValue /
        (max(abs(calc.openPrice - calc.stopLoss), 0.00001))
    )
    # Кол-во покупки
    count_bet = value_bet / LOT

    if calc.currency == calc.forexInfo.pair[1]:
        value_bet *= calc.openPrice
    elif calc.currency == calc.forexInfo.pair[0]:
        count_bet *= calc.stopLoss
        value_bet = count_bet * LOT
    else:
        BASExxx = f'{calc.currency}/{calc.forexInfo.pair[1]}'
        yyyBASE = f'{calc.forexInfo.pair[0]}/{calc.currency}'
        count_bet *= calc.forexInfo.cross_prices.get(BASExxx, 1)
        value_bet = count_bet * LOT * \
            calc.forexInfo.cross_prices.get(yyyBASE, 1)

    conclusion = ''
    p_show = ''

    if saved:
        profit_info = get_html_from_calc_results(user_id, calc)
    else:
        p_show = ''
        conclusion = ''
        for i in range(len(calc.tpRatio)):
            rate = 1
            tp_ratio_i = calc.tpRatio[i]
            tp_i = max(calc.openPrice + (calc.openPrice -
                                         calc.stopLoss) * tp_ratio_i, 0)

            percent_show = ''
            coins_show = ''
            tp_class = ''
            if calc.splitValues is not None and len(calc.splitValues) != 0:
                percent = calc.splitValues[i]
                rate = percent / 100
                count = get_print_float(count_bet * rate, 2)

                tp_class = 'tp_item'
                percent_show = f'{get_print_float(percent, round_count)}%'
                coins_show = f'<b>{count} {point[lang]["lot"]}</b>'

            conclusion += f'<div>'
            conclusion += f'{get_print_float(tp_i, round_count)} {trading_currency} (x{tp_ratio_i})'
            conclusion += f'</div>'

            profit = abs(calc.openPrice - tp_i) * \
                rate * count_bet * pow(10, 5)
            if calc.forexInfo.pair[0] == calc.currency:
                profit /= calc.stopLoss
            elif calc.forexInfo.pair[1] != calc.currency:
                profit /= calc.forexInfo.cross_prices.get(
                    f'{calc.currency}/{calc.forexInfo.pair[1]}', 1
                )

            p_show += f'<span calss="value">{get_print_float(profit, round_count)}</span>'

        profit_info = f"""
            <div class="block">
                <p class="name">{point[lang]['conclusion']}</p>
                <div class="tp">
                    {conclusion}
                </div>
            </div>
            <div class="block">
                <p class="name">{point[lang]['profit']} (<b>{calc.currency}</b>)</p>
				<div class="profit">
                    {p_show}
                </div>
            </div>
        """

    trading_type = 'buy' if calc.openPrice > calc.stopLoss else 'sell'
    saved = '' if not calc.inStat else """
<svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <rect width="20" height="20" rx="4" fill="#06BD32" />
    <path
        d="M8.33333 11.3333L13.25 6.41667C13.4028 6.26389 13.5972 6.1875 13.8333 6.1875C14.0694 6.1875 14.2639 6.26389 14.4167 6.41667C14.5694 6.56944 14.6458 6.76389 14.6458 7C14.6458 7.23611 14.5694 7.43056 14.4167 7.58333L8.91666 13.0833C8.75 13.25 8.55555 13.3333 8.33333 13.3333C8.11111 13.3333 7.91666 13.25 7.75 13.0833L5.58333 10.9167C5.43055 10.7639 5.35416 10.5694 5.35416 10.3333C5.35416 10.0972 5.43055 9.90278 5.58333 9.75C5.73611 9.59722 5.93055 9.52083 6.16666 9.52083C6.40278 9.52083 6.59722 9.59722 6.75 9.75L8.33333 11.3333Z"
        fill="white" />
</svg>"""

    return f"""
<header class="header">
    <div class="header_name">
        <div class="title">{pair}</div>
        <div class="market">- Форекс</div>
    </div>
</header>
<div class="major">
    <div class="name">Купите:</div>
    <div class="value">{get_print_float(count_bet)} {point[lang]["lot"]}</div>
</div>

<div class="content">
    <div class="block">
        <div class="name">Цена:</div>
        <div class="value">{get_print_float(calc.openPrice, round_count)} {trading_currency}</div>
    </div>
    <div class="block">
        <div class="name">Стоп:</div>
        <div class="value">{get_print_float(calc.newStop or calc.stopLoss, round_count)} {trading_currency}</div>
    </div>
    <div class="block">
        <div class="name">Тейк-профит:</div>
        <div class="value list">
            {conclusion}
        </div>
    </div>
    <div class="block">
        <div class="name">Прибыль (USDT):</div>
        <div class="profit">
            {p_show}
        </div>
    </div>
</div>
"""
    # <div class="point">
    #     <p class="name">{point[lang]['dep']}</p>
    #     <p class="value">{get_print_float(calc.deposit)} {calc.currency}</p>
    # </div>
    # {(
    #     '<div class="point">'
    #         f'<p class="name">{point[lang]["style"]}</p>'
    #         f'<p class="value">{trading_style}</p>'
    #     '</div>'
    #     ) if trading_style != '' else ''
    # }


def get_html_from_calc_results(
    user_id: int,
    calc: Calculation,
):
    lang = get_lang(user_id)

    point = {
        'ru': {
            'deposit': 'Итоговый депозит',
            'sum': 'Профит от сделки',
            'takes': 'Тейки',
            'stops': 'Стопы',
        },
        'en': {
            'deposit': 'Final deposit',
            'sum': 'Deal profit',
            'takes': 'Take profits',
            'stops': 'Stop losses',
        },
    }

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    saved_stats = db.get_calculations_by_user(user_db_id, True)
    tp_count = 0
    sl_count = 0
    for stat in saved_stats:
        stat_profit = stat.profit or 0

        if stat_profit > 0:
            tp_count += round(stat_profit / stat.riskValue)
        if stat_profit < 0:
            sl_count += round(abs(stat_profit) / stat.riskValue, 1)

    deposit = (u_base.deposit if u_base is not None else 0) or 0
    profit = calc.profit or 0.

    return f"""
<div class="row">
    <div class="block">
        <div class="value">{get_print_float(profit, calc.roundCount)} {calc.currency}</div>
        <div class="name">{point[lang]['sum']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(deposit, calc.roundCount)} {calc.currency}</div>
        <div class="name">{point[lang]['deposit']}</div>
    </div>
</div>
<div class="row">
    <div class="block">
        <div class="value">{get_print_float(tp_count, 0)}</div>
        <div class="name">{point[lang]['takes']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(sl_count, 1)}</div>
        <div class="name">{point[lang]['stops']}</div>
    </div>
</div>
"""


def getTrailingStopsMessage(lang: Literal['ru', 'en'], value: Optional[list[CalcTrailingStop]], openPrice: float, stopLoss: float):
    trailing_stops = ''
    if value:
        for el in value:
            dt = datetime.fromisoformat(
                el.createdAt.replace('Z', '')
            ) + timedelta(hours=3)
            time = dt.strftime("%H:%M")

            trailing_stops += f'\n{time} - '
            trailing_stops += 'Передвинул стоп к ' if lang == 'ru' else 'Moved the stop to '

            if el.value == openPrice:
                trailing_stops += 'безубытку' if lang == 'ru' else 'breakeven'
            else:
                valueCount = (
                    (el.value - openPrice) /
                    (openPrice - stopLoss)
                )

                trailing_stops += get_print_float(el.value)
                trailing_stops += f' ({getStrValueCount(valueCount, lang)})'

    return trailing_stops


def getStrValueCount(count: float, lang: LANGUAGES_TYPE = 'ru'):
    if count == 0:
        if lang == 'ru':
            return 'безубыток'
        else:
            return 'breakeven'

    plus = ''
    if count > 0:
        plus = '+'

    tp_sl = ''

    if lang == 'ru':
        if count > 0:
            tp_sl = getNounByNumber(count, 'тейк', 'тейка', 'тейков')
        else:
            tp_sl = getNounByNumber(count, 'стоп', 'стопа', 'стопов')
    else:
        if count > 0 and count <= 1:
            tp_sl = 'take'
        elif count > 1:
            tp_sl = 'takes'
        elif count >= -1 and count < 0:
            tp_sl = 'stop'
        else:
            tp_sl = 'stops'

    return f'{plus}{get_print_float(count, 1)} {tp_sl}'
