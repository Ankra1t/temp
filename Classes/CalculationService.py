from telebot import TeleBot

# from CALCULATE.callbacks.stats.keyboards import kb_freeze_calc
from CALCULATE.common.messages import msg_freeze_calc
from CALCULATE.states import StatsState

from db import Database
from common.dt import get_datetime_now
from models import MARKETS_TYPE, CalculatorStats
from .CurrencyService import CurrencyService


class CalculationService():
    def __init__(self, db: Database, currencyService: CurrencyService) -> None:
        self.db = db
        self.currencyService = currencyService

    def set_profit(self, bot: TeleBot, stat_id: int, value: float):
        # Выставляем значение профита в статистику
        self.db.set_calculation_profit(stat_id, value)
        self.db.set_calculation_in_stat(stat_id, True)

        # Находим данный расчет по статистике
        calc_info = self.db.get_calculation(stat_id)
        if calc_info is None:
            return

        # Проверка настроек пользователя
        # Если не выставлен риск на день, то ничего не делаем
        user_settings = self.db.get_calc_user_settings(calc_info.user_id)

        if user_settings and user_settings.is_updating_deposit:
            self.db.set_user_base(
                calc_info.user_id, 'base_deposit',
                (user_settings.deposit or 0.) + (calc_info.profit or 0.)
            )

        if value >= 0:
            return

        day_risk = None
        deposit = None
        currency = 'USD'
        if user_settings is not None:
            day_risk = user_settings.day_risk
            deposit = user_settings.deposit
            currency = user_settings.currency or 'USD'

        if day_risk is None or (day_risk[1] and deposit is None):
            return
        elif day_risk[1]:
            day_risk_value = (deposit or 0) * day_risk[0] * 0.01
        else:
            day_risk_value = day_risk[0]

        # Ищем все сохраненные подсчеты пользователя
        user_calculations = self.db.get_calculations_by_user(
            calc_info.user_id, True
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
            user_info = self.db.get_user_by_id(calc_info.user_id)
            if user_info is None:
                return

            diff = abs(today_profit) - day_risk_value
            if day_risk[1]:
                diff = diff / (deposit or 1)

            tg_id = user_info.tg_id
            bot.send_message(
                tg_id, msg_freeze_calc(tg_id, diff, currency, day_risk[1]),
                # reply_markup=kb_freeze_calc(tg_id)
            )
            bot.set_state(tg_id, StatsState.freeze)

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

        if market == 'crypto':
            currencies_price = False
        else:
            stats_currencies = self.db.get_calculations_currencies(
                user_db_id, True, market
            )
            pairs = list(map(lambda cur: f'{base_currency}/{cur}', stats_currencies.keys()))
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
                rate = currencies_price.get(f'{base_currency}/{stat.currency}', 1.)

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
