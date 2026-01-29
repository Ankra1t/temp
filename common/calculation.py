from datetime import datetime, timedelta
from typing import Literal, Optional
from common.utils import get_print_float, getNounByNumber

from models import LANGUAGES_TYPE, CalcTrailingStop, Calculation, CalculationResult


def get_count_value_bet(calc: Calculation, lot=pow(10, 5)):
    """Возвращает кол-во и сумму покупки, коэффициент спота"""
    spot_rate = 1
    diff_op_sl = calc.openPrice - calc.stopLoss

    if calc.market == 'forex' and calc.forexInfo is not None:
        value_bet = calc.riskValue / abs(diff_op_sl)
        count_bet = value_bet / lot

        if calc.currency == calc.forexInfo.pair[1]:
            value_bet *= calc.openPrice
        elif calc.currency == calc.forexInfo.pair[0]:
            count_bet *= calc.stopLoss
            value_bet = count_bet * lot
        else:
            prices = calc.forexInfo.cross_prices

            BASExxx = f'{calc.currency}/{calc.forexInfo.pair[1]}'
            yyyBASE = f'{calc.forexInfo.pair[0]}/{calc.currency}'

            count_bet *= prices.get(BASExxx, 1)
            value_bet = count_bet * lot * prices.get(yyyBASE, 1)
    else:
        count_bet = calc.riskValue / abs(diff_op_sl)
        value_bet = count_bet * calc.openPrice

    if calc.tradingType == 'spot' and value_bet > calc.deposit:
        spot_rate = calc.deposit / value_bet

        count_bet *= spot_rate
        value_bet = calc.deposit

    return count_bet, value_bet, spot_rate


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
    count = float(get_print_float(count, 1))

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


def get_result(calc: Calculation):
    count_bet, value_bet, _ = get_count_value_bet(calc)

    fee = value_bet
    value_bet += fee

    tp_values: list[float] = []
    profit_values: list[float] = []
    profit_rate_values: list[float] | None = None

    tp_count = len(calc.tpRatio)

    is_splitting = (
        calc.splitValues is not None and
        len(calc.splitValues) != 0 and
        len(calc.splitValues) == tp_count
    )

    if is_splitting:
        profit_rate_values = []

    for i in range(tp_count):
        tp_ratio_i = calc.tpRatio[i]

        diff_op_sl = calc.openPrice - calc.stopLoss
        tp_i = max(
            calc.openPrice + diff_op_sl * tp_ratio_i,
            0
        )
        tp_values.append(tp_i)

        profit_rate_i = 1
        if is_splitting:
            profit_rate_i = calc.splitValues[i] * 0.01  # type: ignore
            profit_rate_values.append(profit_rate_i)  # type: ignore

        profit_i = abs(calc.openPrice - tp_i) * count_bet * profit_rate_i

        if calc.market == 'forex' and calc.forexInfo is not None:
            profit_i *= pow(10, 5)
            if calc.forexInfo.pair[0] == calc.currency:
                profit_i /= calc.stopLoss
            elif calc.forexInfo.pair[1] != calc.currency:
                profit_i /= calc.forexInfo.cross_prices.get(
                    f'{calc.currency}/{calc.forexInfo.pair[1]}', 1
                )

        profit_values.append(profit_i - 2 * fee)

    return CalculationResult(
        count_bet=count_bet,
        value_bet=value_bet,

        tp_count=tp_count,
        profit_rate_values=profit_rate_values,
        profit_values=profit_values,
        tp_values=tp_values,

        exchange=None,
        fee=fee or None,
    )
