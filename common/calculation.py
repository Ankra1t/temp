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
            'buy': 'Покупаем',
            'style': 'Стиль торговли',
            'profit': 'Прибыль',
            'coin': 'монет',
        },
        'en': {
            'dep': 'Deposit',
            'risk': 'Risk',
            'open': 'Price',
            'sl': 'Stop',
            'conclusion': 'Take-profit',
            'buy': 'Buying',
            'style': 'Trading style',
            'profit': 'Profit',
            'coin': 'tokens',
        }
    }

    trading_style = (calc.trading_style or '').capitalize()

    # Округление
    round_count = calc.round_count or 5

    # Кол-во покупки
    count_bet = (
        calc.risk_value /
        max(abs(calc.open_price - calc.stop_loss), 0.0001)
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
            tp_i = get_print_float(
                max(calc.open_price + (calc.open_price -
                    calc.stop_loss) * tp_ratio_i, 0),
                round_count
            )

            split = ''
            rate = 1
            if calc.split_values is not None and len(calc.split_values) != 0:
                percent = calc.split_values[i]
                rate = percent / 100
                count = get_print_float(count_bet * rate, 2)

                split = f' (<b>{count} {point[lang]["coin"]}</b>) — {get_print_float(percent, round_count)}%'

            conclusion += f'<div style="white-space: nowrap;"><b>x{tp_ratio_i}</b>: <u>{tp_i} {calc.currency}</u> {split}</div>'
            p_show += f'<p class="value">{get_print_float(abs(calc.open_price - tp_i) * rate * count_bet, round_count)}</p>'

        if calc.split_values is not None and len(calc.split_values) != 0:
            conclusion = f'<div style="flex: 0 0 100%;">{conclusion}</div>'

        profit_info = f"""
            <div class="block">
                <div class="point tp">
                    <p class="name">{point[lang]['conclusion']}</p>
                    {conclusion}
                </div>
            </div>
            <div class="block">
                <div class="point profit">
                    <p class="name">{point[lang]['profit']} (<b>{calc.currency}</b>)</p>
                    {p_show}
                </div>
            </div>
        """

    tool = calc.tool or 'BTC/USDT'

    return f"""
<div class="title">{tool}</div>
<div class="block">
    <div class="inline_block">
        <div class="point">
            <p class="name">{point[lang]['dep']}</p>
            <p class="value">{get_print_float(calc.deposit)} {calc.currency}</p>
        </div>
        <div class="point">
            <p class="name">{point[lang]['risk']}</p>
            <p class="value">{get_print_float(calc.risk_value)} {calc.currency}</p>
        </div>
    </div>
    {(
        '<div class="point">'
            f'<p class="name">{point[lang]["style"]}</p>'
            f'<p class="value">{trading_style}</p>'
        '</div>'
        ) if trading_style != '' else ''
    }
</div>
<div class="block">
    <div class="inline_block">
        <div class="point">
            <p class="name">{point[lang]['open']}</p>
            <p class="value">{get_print_float(calc.open_price, round_count)} {calc.currency}</p>
        </div>
        <div class="point">
            <p class="name">{point[lang]['sl']}</p>
            <p class="value">{get_print_float(calc.stop_loss, round_count)} {calc.currency}</p>
        </div>
    </div>
    <div class="point">
        <p class="name">{point[lang]['buy']}</p>
        <p class="value">
            {get_print_float(count_bet)} {point[lang]["coin"]}
        </p>
        <p class="value">
            ({get_print_float(value_bet)} {calc.currency})
        </p>
    </div>
</div>
{profit_info}
"""


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
            'buy': 'Покупаем',
            'style': 'Стиль торговли',
            'profit': 'Прибыль',
            'lot': 'лота',
        },
        'en': {
            'dep': 'Deposit',
            'risk': 'Risk',
            'open': 'Price',
            'sl': 'Stop',
            'conclusion': 'Take-profit',
            'buy': 'Buying',
            'style': 'Trading style',
            'profit': 'Profit',
            'lot': 'lots',
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
        (max(abs(calc.open_price - calc.stop_loss), 0.0001))
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
            tp_i = get_print_float(
                max(calc.open_price + (calc.open_price -
                    calc.stop_loss) * tp_ratio_i, 0),
                round_count
            )

            split = ''
            if calc.split_values is not None and len(calc.split_values) != 0:
                percent = calc.split_values[i]
                rate = percent / 100
                count = get_print_float(count_bet * rate, 2)

                split = f' (<b>{count} {point[lang]["lot"]}</b>) — {get_print_float(percent, round_count)}%'

            conclusion += f'<div style="white-space: nowrap;"><b>x{tp_ratio_i}</b>: <u>{tp_i} {trading_currency}</u> {split}</div>'

            profit = abs(calc.open_price - tp_i) * \
                rate * count_bet * pow(10, 5)
            if calc.forex_info.pair[0] == calc.currency:
                profit /= calc.stop_loss
            elif calc.forex_info.pair[1] != calc.currency:
                profit /= calc.forex_info.cross_prices.get(
                    f'{calc.currency}/{calc.forex_info.pair[1]}', 1
                )

            p_show += f'<p class="value">{get_print_float(profit, round_count)}</p>'

        if calc.split_values is not None and len(calc.split_values) != 0:
            conclusion = f'<div style="flex: 0 0 100%;">{conclusion}</div>'

        profit_info = f"""
            <div class="block">
                <div class="point tp">
                    <p class="name">{point[lang]['conclusion']}</p>
                    {conclusion}
                </div>
            </div>
            <div class="block">
                <div class="point profit">
                    <p class="name">{point[lang]['profit']} (<b>{calc.currency}</b>)</p>
                    {p_show}
                </div>
            </div>
        """

    return f"""
        <div class="title">{pair}</div>
        <div class="block">
            <div class="inline_block">
                <div class="point">
                    <p class="name">{point[lang]['dep']}</p>
                    <p class="value">{get_print_float(calc.deposit)} {calc.currency}</p>
                </div>
                <div class="point">
                    <p class="name">{point[lang]['risk']}</p>
                    <p class="value">{get_print_float(calc.risk_value)} {calc.currency}</p>
                </div>
            </div>
            {(
                '<div class="point">'
                    f'<p class="name">{point[lang]["style"]}</p>'
                    f'<p class="value">{trading_style}</p>'
                '</div>'
                ) if trading_style != '' else ''
            }
        </div>
        <div class="block">
            <div class="inline_block">
                <div class="point">
                    <p class="name">{point[lang]['open']}</p>
                    <p class="value">{get_print_float(calc.open_price, round_count)} {trading_currency}</p>
                </div>
                <div class="point">
                    <p class="name">{point[lang]['sl']}</p>
                    <p class="value">{get_print_float(calc.stop_loss, round_count)} {trading_currency}</p>
                </div>
            </div>
            <div class="point">
                <p class="name">{point[lang]['buy']}</p>
                <p class="value">
                    {get_print_float(count_bet)} {point[lang]["lot"]}
                </p>
                <p class="value">
                    ({get_print_float(value_bet)} {calc.currency})
                </p>
            </div>
        </div>
        {profit_info}
    """


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
            'deposit': 'The final deposit',
            'sum': 'Deal profit',
            'sl': 'Stop-loss',
            'tp': 'Take-profit',
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
        <div class="block">
            <div class="point">
                <p class="name">{point[lang]['sum']}</p>
                <p class="value">{get_print_float(profit, calc.round_count)} {calc.currency}</p>
            </div>
            <div class="point">
                <p class="name">{point[lang]['deposit']}</p>
                <p class="value">{get_print_float(deposit, calc.round_count)} {calc.currency}</p>
            </div>
            <div class="point">
                <p class="name">{point[lang]['takes']}</p>
                <p class="value">{get_print_float(tp_count, 0)}</p>
            </div>
            <div class="point">
                <p class="name">{point[lang]['stops']}</p>
                <p class="value">{get_print_float(sl_count, 1)}</p>
            </div>
        </div>
    """


def get_tool_of_calc(calc: Calculation):
    result = 'NO'

    if calc.market == 'crypto':
        result = calc.tool or 'BTC/USDT'
    elif calc.market == 'forex' and calc.forex_info is not None:
        result = ''.join(calc.forex_info.pair)

    return '#' + result.replace('/', '').lower()
