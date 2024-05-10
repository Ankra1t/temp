from common.utils import get_lang, get_print_float

from models import Calculation
from db import db


def get_html_from_calc(user_id: int, calc: Calculation, saved=False):
    if calc.forex_info is not None:
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
            'sl': 'Stop',
            'conclusion': 'Take-profit',
            'count': 'Count',
            'sum': 'Sum',
            'style': 'Trading style',
            'profit': 'Profit',
            'coin': 'tokens',
            'buy': 'Buy',
            'sell': 'Sell',
        }
    }

    trading_style = (calc.trading_style or '').capitalize()

    # Округление
    round_count = calc.round_count or 5

    # Кол-во покупки
    count_bet = (
        calc.risk_value /
        max(abs(calc.open_price - calc.stop_loss), 0.00001)
    )

    # Сумма покупки
    value_bet = count_bet * calc.open_price

    if saved:
        profit_info = get_html_from_calc_results(user_id, calc)
    else:
        p_show = ''
        conclusion = ''
        for i in range(len(calc.tp_ratio)):
            tp_ratio_i = calc.tp_ratio[i]
            tp_i = max(
                calc.open_price +
                (calc.open_price - calc.stop_loss) * tp_ratio_i,
                0
            )

            tp_class = 'tp_default'
            coins_show = ''
            percent_show = ''
            rate = 1
            if calc.split_values is not None and len(calc.split_values) != 0:
                percent = calc.split_values[i]
                rate = percent / 100
                count = get_print_float(count_bet * rate, 2)

                tp_class = 'tp_item'
                percent_show = f'{get_print_float(percent, round_count)}%'
                coins_show = f'<b>{count} {point[lang]["coin"]}</b>'

            conclusion += f'<div class="{tp_class}">'
            conclusion += f'<div class="tp_val"><b>x{tp_ratio_i}</b> {percent_show}</div>'
            conclusion += f'<div class="tp_count"><u>{get_print_float(tp_i, round_count)} {calc.currency}</u> {coins_show}</div>'
            conclusion += f'</div>'

            p_show += f'<p class="value">{get_print_float(abs(calc.open_price - tp_i) * rate * count_bet, round_count)}</p>'

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
    trading_type = 'buy' if calc.open_price < calc.stop_loss else 'sell'
    saved = '' if not calc.in_stat else """
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
        <div class="value">{get_print_float(calc.risk_value)} {calc.currency}</div>
        <div class="name">{point[lang]['risk']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(calc.open_price, round_count)} {calc.currency}</div>
        <div class="name">{point[lang]['open']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(calc.stop_loss, round_count)} {calc.currency}</div>
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

def get_msg_of_calc(user_id: int, calc: Calculation):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'style': 'Стиль торговли'
        },
        'en': {
            'style': 'Trading style'
        },
    }

    result = 'NO'

    if calc.market == 'crypto':
        result = calc.tool or 'BTC/USDT'
    elif calc.market == 'forex' and calc.forex_info is not None:
        result = ''.join(calc.forex_info.pair)

    style = ''
    if calc.trading_style is not None:
        style = f'{texts[lang]["style"]}: <b>{calc.trading_style}</b>'

    return f"""{style}
#{result.replace('/', '').lower()}"""


def get_count_value_bet(calc: Calculation, lot=pow(10, 5)):
    """Возвращает кол-во и сумму покупки, коэффициент спота"""
    spot_rate = 1

    if calc.market == 'forex' and calc.forex_info is not None:
        value_bet = (
            calc.risk_value / abs(calc.open_price - calc.stop_loss)
        )
        count_bet = value_bet / lot

        if calc.currency == calc.forex_info.pair[1]:
            value_bet *= calc.open_price
        elif calc.currency == calc.forex_info.pair[0]:
            count_bet *= calc.stop_loss
            value_bet = count_bet * lot
        else:
            BASExxx = f'{calc.currency}/{calc.forex_info.pair[1]}'
            yyyBASE = f'{calc.forex_info.pair[0]}/{calc.currency}'
            count_bet *= calc.forex_info.cross_prices.get(BASExxx, 1)
            value_bet = count_bet * lot * \
                calc.forex_info.cross_prices.get(yyyBASE, 1)
    else:
        count_bet = calc.risk_value / abs(calc.open_price - calc.stop_loss)
        value_bet = count_bet * calc.open_price

    if calc.trading_type == 'spot' and value_bet > calc.deposit:
        spot_rate = calc.deposit / value_bet

        count_bet *= spot_rate
        value_bet = calc.deposit

    return count_bet, value_bet, spot_rate


def get_html_from_forex_calc(
    user_id: int,
    calc: Calculation,
    saved=False,
):
    if calc.forex_info is None:
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
            'sl': 'Stop',
            'conclusion': 'Take-profit',
            'count': 'Count',
            'sum': 'Sum',
            'style': 'Trading style',
            'profit': 'Profit',
            'lot': 'lots',
            'buy': 'Buy',
            'sell': 'Sell',
        }
    }

    pair = '/'.join(calc.forex_info.pair)
    LOT = pow(10, 5)

    trading_style = (calc.trading_style or '').capitalize()

    # Валюта торговли
    trading_currency = calc.forex_info.pair[1]

    # Округление
    round_count = calc.round_count or 5

    # Сумма покупки
    value_bet = (
        calc.risk_value /
        (max(abs(calc.open_price - calc.stop_loss), 0.00001))
    )
    # Кол-во покупки
    count_bet = value_bet / LOT

    if calc.currency == calc.forex_info.pair[1]:
        value_bet *= calc.open_price
    elif calc.currency == calc.forex_info.pair[0]:
        count_bet *= calc.stop_loss
        value_bet = count_bet * LOT
    else:
        BASExxx = f'{calc.currency}/{calc.forex_info.pair[1]}'
        yyyBASE = f'{calc.forex_info.pair[0]}/{calc.currency}'
        count_bet *= calc.forex_info.cross_prices.get(BASExxx, 1)
        value_bet = count_bet * LOT * \
            calc.forex_info.cross_prices.get(yyyBASE, 1)

    if saved:
        profit_info = get_html_from_calc_results(user_id, calc)
    else:
        p_show = ''
        conclusion = ''
        for i in range(len(calc.tp_ratio)):
            rate = 1
            tp_ratio_i = calc.tp_ratio[i]
            tp_i = max(calc.open_price + (calc.open_price -
                                          calc.stop_loss) * tp_ratio_i, 0)

            percent_show = ''
            coins_show = ''
            tp_class = ''
            if calc.split_values is not None and len(calc.split_values) != 0:
                percent = calc.split_values[i]
                rate = percent / 100
                count = get_print_float(count_bet * rate, 2)

                tp_class = 'tp_item'
                percent_show = f'{get_print_float(percent, round_count)}%'
                coins_show = f'<b>{count} {point[lang]["lot"]}</b>'

            conclusion += f'<div>'
            conclusion += f'{get_print_float(tp_i, round_count)} {trading_currency} (x{tp_ratio_i})'
            conclusion += f'</div>'

            profit = abs(calc.open_price - tp_i) * \
                rate * count_bet * pow(10, 5)
            if calc.forex_info.pair[0] == calc.currency:
                profit /= calc.stop_loss
            elif calc.forex_info.pair[1] != calc.currency:
                profit /= calc.forex_info.cross_prices.get(
                    f'{calc.currency}/{calc.forex_info.pair[1]}', 1
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

    trading_type = 'buy' if calc.open_price > calc.stop_loss else 'sell'
    saved = '' if not calc.in_stat else """
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
        <div class="value">{get_print_float(calc.open_price, round_count)} {trading_currency}</div>
    </div>
    <div class="block">
        <div class="name">Стоп:</div>
        <div class="value">{get_print_float(calc.stop_loss, round_count)} {trading_currency}</div>
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
            'takes': 'Take-profits',
            'stops': 'Stop-losses',
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
            tp_count += round(stat_profit / stat.risk_value)
        if stat_profit < 0:
            sl_count += round(abs(stat_profit) / stat.risk_value, 1)

    deposit = (u_base.deposit if u_base is not None else 0) or 0
    profit = calc.profit or 0.

    return f"""
<div class="row">
    <div class="block">
        <div class="value">{get_print_float(profit, calc.round_count)} {calc.currency}</div>
        <div class="name">{point[lang]['sum']}</div>
    </div>
    <div class="block">
        <div class="value">{get_print_float(deposit, calc.round_count)} {calc.currency}</div>
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