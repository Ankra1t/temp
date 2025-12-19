from datetime import datetime, timedelta
from typing import Literal, Optional
from common.utils import get_print_float, getNounByNumber

from models import LANGUAGES_TYPE, CalcTrailingStop, Calculation


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
