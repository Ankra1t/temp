from datetime import datetime
from common.utils import get_decimal_count, get_lang, get_print_float
from common.dt import get_datetime_now

from data.data import liteDb
from db import Database
from service import user_settings_storage
from models import MARKETS_TYPE, Calculation, CalculationResult, CalculatorStats
from services import calculation, channel_calc

from .CurrencyService import CurrencyService


transl_market = {
    'ru': {
        'crypto': 'Криптовалюты',
        'paper': 'Акции',
        'forex': 'Форекс',
        'RF': 'РФ',
        'USA': 'США',
    },
    'en': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    },
    'uz': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    },
    'tr': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    },
}


trading_type_translates = {
    'ru': {
        'margin': 'маржинальный',
        'spot': 'спотовый',
    },
    'en': {
        'margin': 'margin',
        'spot': 'spot',
    },
    'uz': {
        'margin': 'marjasi',
        'spot': 'sple',
    },
    'tr': {
        'margin': 'marj',
        'spot': 'spot',
    },
}


class CalculationService():
    def __init__(self, db: Database, currencyService: CurrencyService) -> None:
        self.db = db
        self.currencyService = currencyService
    # !deprecated

    def set_profit(self, tgId: int, calc_id: int, value: float):
        # Находим данный расчет по статистике
        calc_info = calculation.get(userId=1, calcId=calc_id)
        send_data = channel_calc.getByCalc(calc_id)
        if calc_info is None or (calc_info.ActiveCalc is not None and send_data is None):
            return

        # Выставляем значение профита в статистику
        self.db.set_calculation_profit(calc_id, value)
        self.db.set_calculation_in_stat(calc_id, True)

        # Находим данный расчет по статистике
        calc_info = calculation.get(userId=1, calcId=calc_id)
        if calc_info is None:
            return

        # Проверка настроек пользователя
        # Если не выставлен риск на день, то ничего не делаем
        user_settings = user_settings_storage.get_or_create(tgId)

        if user_settings and user_settings.is_updating_deposit:
            user_settings_storage.set_deposit(
                tgId, (user_settings.deposit or 0.) + (calc_info.profit or 0.))

    def get_stats(self, tg_id: int, market: MARKETS_TYPE | None = None):
        user_db_id = self.db.get_user_id_by_tg_id(tg_id)
        user_market_base = user_settings_storage.get_or_create(tg_id)

        base_currency = 'USDT' if market == 'crypto' else 'USD'
        if user_market_base is not None:
            base_currency = user_market_base.currency or base_currency

        all_stats = self.db.get_calculations_by_user(
            user_db_id,
            market=market
        )
        saved_stats = self.db.get_calculations_by_user(
            user_db_id, True,
            market=market
        )

        tp_count = 0
        sl_count = 0

        if market != 'forex':
            currencies_price = False
        else:
            stats_currencies = self.db.get_calculations_currencies(
                user_db_id, True, market
            )
            pairs = list(
                map(
                    lambda cur: f'{base_currency}/{cur}',
                    stats_currencies.keys()
                )
            )
            currencies_price = self.currencyService.getPairsPrice(pairs)

        profit = 0
        max_profit = 0.
        min_loss = 0.
        for stat in saved_stats:
            stat_profit = stat.profit or 0

            if stat_profit > 0:
                tp_count += round(stat_profit / stat.riskValue, 1)
            if stat_profit < 0:
                sl_count += round(abs(stat_profit) / stat.riskValue, 1)

            rate = 1.
            if currencies_price:
                rate = currencies_price.get(
                    f'{base_currency}/{stat.currency}', 1.
                )

            base_profit = stat_profit / rate

            if base_profit > 0:
                max_profit = max(base_profit, max_profit)
            else:
                min_loss = min(base_profit, min_loss)

            profit += base_profit

        return CalculatorStats(
            currency=base_currency,
            profit=profit,
            tp_count=round(tp_count, 1),
            sl_count=round(sl_count, 1),
            all_stats_count=len(all_stats),
            saved_stats_count=len(saved_stats),
            max_profit=max_profit,
            min_loss=min_loss
        )

    def check_day_risk(self, user_id: int, market: MARKETS_TYPE):
        user_db_id = self.db.get_user_id_by_tg_id(user_id)
        user_settings = user_settings_storage.get_or_create(user_id)
        if user_settings is None or user_settings.day_risk is None:
            return False

        day_risk = user_settings.day_risk
        deposit = user_settings.deposit
        currency = user_settings.currency or (
            'USDT' if market == 'crypto' else 'USD')

        if day_risk[1] and deposit is None:
            return False
        elif day_risk[1]:
            day_risk_value = (deposit or 0) * day_risk[0] * 0.01
        else:
            day_risk_value = day_risk[0]

        # Ищем все сохраненные расчеты пользователя
        user_calculations = self.db.get_calculations_by_user(
            user_db_id, True, market
        )

        today = get_datetime_now().date()
        today_profit = 0

        # Считаем профит за день
        for calc in user_calculations:
            if calc.status != 'FINISH' or calc.statDt is None:
                continue

            if datetime.fromisoformat(calc.statDt.replace('Z', '')).date() == today:
                today_profit += calc.profit or 0

        # Если профит положительный и меньше риска на день, отправляем предупреждение
        if today_profit > 0 or abs(today_profit) < day_risk_value:
            return False

        unit = currency
        diff = abs(today_profit) - day_risk_value
        if day_risk[1]:
            unit = '%'
            diff /= (deposit or 1)
        diff = get_print_float(diff)

        return f'{diff} {unit}'

    def get_count_value_bet(self, calc: Calculation, lot=pow(10, 5)):
        spot_rate = 1.

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

    def get_result(self, calc: Calculation):
        exchange_fee = liteDb.getCalc(calc.id)
        fee_rate = exchange_fee[1] if exchange_fee is not None else 0
        fee_rate /= 100

        count_bet, value_bet, _ = self.get_count_value_bet(calc)

        fee = value_bet * fee_rate
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

            exchange=exchange_fee[0] if exchange_fee is not None else None,
            fee=fee or None,
        )

    def html_calculation(
        self,
        user_id: int,
        calc: Calculation,
    ):
        lang = get_lang(user_id)

        is_saved = calc.status == 'FINISH'
        calc_result = self.get_result(calc)

        texts = {
            'ru': {
                'dep': 'Депозит' if not is_saved else 'Итоговый депозит',
                'risk': 'Риск',
                'open': 'Цена',
                'sl': 'Стоп',

                'conclusion': 'Тейк-профит',
                'profit': 'Прибыль',
                'buy': 'Купите' if not is_saved else 'Было куплено',
                'sum': 'Сумма',
                'style': 'Стиль торговли',
                'trading_type': 'Тип торговли',

                'coin': 'монеты',
                'paper': 'акций',
                'lot': 'лота',

                'takes': 'Тейки',
                'stops': 'Стопы',

                'long': 'покупка',
                'short': 'продажа',
            },
            'en': {
                'dep': 'Deposit' if not is_saved else 'Final deposit',
                'risk': 'Risk',
                'open': 'Price',
                'sl': 'Stop loss',

                'conclusion': 'Take profit',
                'profit': 'Profit',
                'buy': 'Buy' if not is_saved else 'Bought',
                'sum': 'Sum',
                'style': 'Trading style',
                'trading_type': 'Trading type',

                'coin': 'coins',
                'paper': 'shares',
                'lot': 'lots',

                'takes': 'Take profits',
                'stops': 'Stop losses',

                'long': 'long',
                'short': 'short',
            },
            'uz': {
                'dep': 'Depozit' if not is_saved else 'Yakuniy depozit',
                'risk': 'Xavf',
                'open': 'Narx',
                'sl': 'Stop loss',

                'conclusion': 'Daromad',
                'profit': 'Foyda',
                'buy': 'Sotib olmoq' if not is_saved else 'Sotib olingan',
                'sum': 'So\'m',
                'style': 'Savdo uslubi',
                'trading_type': 'Savdo turi',

                'coin': 'tangalar',
                'paper': 'ulushlar',
                'lot': 'juda ko\'p',

                'takes': 'Qabul qilish',
                'stops': 'To\'xtash-yo\'qotishlar',

                'long': 'long',
                'short': 'short',
            },
            'tr': {
                'dep': 'Depozito' if not is_saved else 'Son depozito',
                'risk': 'Risk',
                'open': 'Fiyat',
                'sl': 'Stop loss',

                'conclusion': 'Kar almak',
                'profit': 'Kâr',
                'buy': 'Satın almak' if not is_saved else 'Satın alınmış',
                'sum': 'Meblağ',
                'style': 'Ticaret tarzı',
                'trading_type': 'Ticaret türü',

                'coin': 'madeni para',
                'paper': 'hisse senetleri',
                'lot': 'çok',

                'takes': 'Karmaşa',
                'stops': 'Durma',

                'long': 'long',
                'short': 'short',
            },
        }

        if calc.market == 'crypto':
            tool_name = texts[lang]["coin"]
        elif calc.market == 'forex':
            tool_name = texts[lang]["lot"]
        else:
            tool_name = texts[lang]["paper"]

        if calc.openPrice > calc.stopLoss:
            long_short = 'long'
        else:
            long_short = 'short'

        # Валюта торговли
        trading_currency = calc.currency

        tool = calc.tool or ''
        if calc.forexInfo is not None and calc.market == 'forex':
            trading_currency = calc.forexInfo.pair[1]
            tool = ''.join(calc.forexInfo.pair)

        trading_style = ''
        if calc.tradingStyle is not None:
            trading_style = f'<b>{texts[lang]["style"]}</b>: {calc.tradingStyle.capitalize()}\n'

        # Округление
        round_count = calc.roundCount or 5
        price_round_count = max(
            get_decimal_count(calc.openPrice),
            get_decimal_count(calc.stopLoss),
            round_count
        )

        # Кол-во и сумма покупки
        count_bet, value_bet = calc_result.count_bet, calc_result.value_bet

        if is_saved:
            saved_mes = '#saved '

            stats = self.get_stats(user_id, calc.market)
            profit = calc.profit or 0.
            profit_info = f"""
<div class="block">
    <div class="name">{texts[lang]['profit']}:</div>
    <div class="value">{get_print_float(profit, round_count)} {calc.currency}</div>
</div>
<div class="block">
    <div class="name">{texts[lang]['takes']}:</div>
    <div class="value"> {stats.tp_count}</div>
</div>
<div class="block">
    <div class="name">{texts[lang]['stops']}:</div>
    <div class="value">{get_print_float(stats.sl_count)}</div>
</div>
"""
        else:
            saved_mes = ''
            p_show = ''
            conclusion = ''
            for i in range(len(calc.tpRatio)):
                tp_ratio = calc.tpRatio[i]
                tp_val = calc_result.tp_values[i]
                p_val = calc_result.profit_values[i]

                conclusion += f'<div>{get_print_float(tp_val, price_round_count)} {trading_currency} (x{tp_ratio})</div>'
                p_show += f'<span class="value">{get_print_float(p_val, round_count)}</span>'

            profit_info = f"""
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
            """

        market = ''
        if calc.market == 'crypto':
            market = 'Крипто' if lang == 'ru' else 'Crypto'
        else:
            market = transl_market[lang][calc.market]

        return (f"""
<header class="header">
    <div class="header_name">
        <div class="title {long_short}">{tool.replace('/USDT', '').upper()}</div>
        <div class="market">- {market}</div>
    </div>
</header>
<div class="content major">
    <div class="block">
        <div class="name">{texts[lang]['buy']}:</div>
        <div class="value">{get_print_float(count_bet)} {tool_name}</div>
    </div>
    <div class="block">
        <div class="name">{texts[lang]['sum']}:</div>
        <div class="value">{get_print_float(value_bet, price_round_count)} {calc.currency}</div>
    </div>
</div>

<div class="content">
    <div class="block">
        <div class="name">{texts[lang]['open']}:</div>
        <div class="value">{get_print_float(calc.openPrice, round_count)} {trading_currency}</div>
    </div>
    <div class="block">
        <div class="name">{texts[lang]['sl']}:</div>
        <div class="value">{get_print_float(calc.newStop or calc.stopLoss, round_count)} {trading_currency}</div>
    </div>
    {profit_info}
</div>
""", f"""#{tool.replace("/USDT", "").upper()} {saved_mes}- {texts[lang][long_short]}

<b>{texts[lang]["dep"]}</b>: {get_print_float(calc.deposit + (calc.profit or 0.))} {calc.currency}
<b>{texts[lang]["risk"]}</b>: {get_print_float(calc.riskValue)} {calc.currency}

<b>{texts[lang]["trading_type"]}</b>: {trading_type_translates[lang][calc.tradingType]}
{trading_style}""")

# Моя биржа
# Шорт = мейкер
# Лонг = тейкер
# При изменении депозита сразу давать возможность вводить
