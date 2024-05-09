from telebot import TeleBot


from db import Database
from common.dt import get_datetime_now
from models import MARKETS_TYPE, Calculation, CalculationResult, CalculatorStats
from .CurrencyService import CurrencyService


class CalculationService():
    def __init__(self, db: Database, currencyService: CurrencyService) -> None:
        self.db = db
        self.currencyService = currencyService

    def set_profit(self, calc_id: int, value: float):
        # Выставляем значение профита в статистику
        self.db.set_calculation_profit(calc_id, value)
        self.db.set_calculation_in_stat(calc_id, True)

        # Находим данный расчет по статистике
        calc_info = self.db.get_calculation(calc_id)
        if calc_info is None:
            return

        # Проверка настроек пользователя
        # Если не выставлен риск на день, то ничего не делаем
        user_settings = self.db.get_calc_user_settings(
            calc_info.user_id, calc_info.market
        )

        if user_settings and user_settings.is_updating_deposit:
            self.db.set_user_base(
                calc_info.user_id, 'base_deposit',
                (user_settings.deposit or 0.) + (calc_info.profit or 0.)
            )

    def get_stats(self, tg_id: int, market: MARKETS_TYPE):
        user_db_id = self.db.get_user_id_by_tg_id(tg_id)
        user_market_base = self.db.get_calc_user_settings(user_db_id, market)

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
                tp_count += round(stat_profit / stat.risk_value)
            if stat_profit < 0:
                sl_count += round(abs(stat_profit) / stat.risk_value, 1)

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
            tp_count=int(tp_count),
            sl_count=round(sl_count, 1),
            all_stats_count=len(all_stats),
            saved_stats_count=len(saved_stats),
            max_profit=max_profit,
            min_loss=min_loss
        )

    def check_day_risk(self, bot: TeleBot, user_id: int, market: MARKETS_TYPE):
        user_settings = self.db.get_calc_user_settings(user_id, market)
        if user_settings is None or user_settings.day_risk is None:
            return

        day_risk = user_settings.day_risk
        deposit = user_settings.deposit
        currency = user_settings.currency or 'USD'

        if day_risk[1] and deposit is None:
            return
        elif day_risk[1]:
            day_risk_value = (deposit or 0) * day_risk[0] * 0.01
        else:
            day_risk_value = day_risk[0]

        # Ищем все сохраненные расчеты пользователя
        user_calculations = self.db.get_calculations_by_user(
            user_id, True, market
        )

        today = get_datetime_now().date()
        today_profit = 0

        # Считаем профит за день
        for calc in user_calculations:
            if not calc.in_stat or calc.stat_dt is None:
                continue

            if calc.stat_dt.date() == today:
                today_profit += calc.profit or 0

        # Если профит отрицательный и больше риска на день, отправляем предупреждение
        if today_profit < 0 and abs(today_profit) > day_risk_value:
            user_info = self.db.get_user_by_id(user_id)
            if user_info is None:
                return

            diff = abs(today_profit) - day_risk_value
            if day_risk[1]:
                diff = diff / (deposit or 1)

            tg_id = user_info.tg_id
            # bot.send_message(
            #     tg_id, msg_freeze_calc(tg_id, diff, currency, day_risk[1]),
            #     # reply_markup=kb_freeze_calc(tg_id)
            # )
            # bot.set_state(tg_id, StatsState.freeze)

    def check_deposit(self, bot: TeleBot, user_id: int, market: MARKETS_TYPE):
        u_settings = self.db.get_calc_user_settings(user_id, market)
        if u_settings is None or u_settings.day_risk is None:
            return

        if u_settings.deposit is None or u_settings.risk is None:
            return

        risk_value = u_settings.risk[0]
        if u_settings.risk[1]:
            risk_value *= u_settings.deposit

        if u_settings.deposit < risk_value:
            # bot.send_message(
            #     user_id, msg_deposit_risk(user_id, market),
            #     reply_markup=kb_deposit_risk(user_id, market)
            # )
            pass

    def get_count_value_bet(self, calc: Calculation, lot=pow(10, 5)):
        spot_rate = 1.

        diff_op_sl = calc.open_price - calc.stop_loss

        if calc.market == 'forex' and calc.forex_info is not None:
            value_bet = calc.risk_value / abs(diff_op_sl)
            count_bet = value_bet / lot

            if calc.currency == calc.forex_info.pair[1]:
                value_bet *= calc.open_price
            elif calc.currency == calc.forex_info.pair[0]:
                count_bet *= calc.stop_loss
                value_bet = count_bet * lot
            else:
                prices = calc.forex_info.cross_prices

                BASExxx = f'{calc.currency}/{calc.forex_info.pair[1]}'
                yyyBASE = f'{calc.forex_info.pair[0]}/{calc.currency}'

                count_bet *= prices.get(BASExxx, 1)
                value_bet = count_bet * lot * prices.get(yyyBASE, 1)
        else:
            count_bet = calc.risk_value / abs(diff_op_sl)
            value_bet = count_bet * calc.open_price

        if calc.trading_type == 'spot' and value_bet > calc.deposit:
            spot_rate = calc.deposit / value_bet

            count_bet *= spot_rate
            value_bet = calc.deposit

        return count_bet, value_bet, spot_rate

    def get_result(self, calc: Calculation):
        count_bet, value_bet, _ = self.get_count_value_bet(calc)

        tp_values: list[float] = []
        profit_values: list[float] = []
        profit_rate_values: list[float] | None = None

        tp_count = len(calc.tp_ratio)

        is_splitting = (
            calc.split_values is not None and
            len(calc.split_values) != 0 and
            len(calc.split_values) == tp_count
        )

        if is_splitting:
            profit_rate_values = []

        for i in range(tp_count):
            tp_ratio_i = calc.tp_ratio[i]

            diff_op_sl = calc.open_price - calc.stop_loss
            tp_i = max(
                calc.open_price + diff_op_sl * tp_ratio_i,
                0
            )
            tp_values.append(tp_i)

            profit_rate_i = 1
            if is_splitting:
                profit_rate_i = calc.split_values[i] * 0.01  # type: ignore
                profit_rate_values.append(profit_rate_i)  # type: ignore

            profit_i = abs(calc.open_price - tp_i) * count_bet * profit_rate_i

            if calc.market == 'forex' and calc.forex_info is not None:
                profit_i *= pow(10, 5)
                if calc.forex_info.pair[0] == calc.currency:
                    profit_i /= calc.stop_loss
                elif calc.forex_info.pair[1] != calc.currency:
                    profit_i /= calc.forex_info.cross_prices.get(
                        f'{calc.currency}/{calc.forex_info.pair[1]}', 1
                    )

            profit_values.append(profit_i)

        return CalculationResult(
            count_bet=count_bet,
            value_bet=value_bet,

            tp_count=tp_count,
            profit_rate_values=profit_rate_values,
            profit_values=profit_values,
            tp_values=tp_values,
        )

