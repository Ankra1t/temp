from telebot import TeleBot

# from CALCULATE.callbacks.stats.keyboards import kb_freeze_calc
from CALCULATE.common.messages import msg_freeze_calc
from CALCULATE.states import StatsState

from db import Database
from common.dt import get_datetime_now
from models import CalculatorStats


class CalculationService():
    def __init__(self, bot: TeleBot, db: Database) -> None:
        self.bot = bot
        self.db = db

    def set_profit(self, stat_id: int, value: float):
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
            self.bot.send_message(
                tg_id, msg_freeze_calc(tg_id, diff, currency, day_risk[1]),
                # reply_markup=kb_freeze_calc(tg_id)
            )
            self.bot.set_state(tg_id, StatsState.freeze)

    def get_stats(self, tg_id: int):
        user_db_id = self.db.get_user_id_by_tg_id(tg_id)

        all_stats = self.db.get_calculations_by_user(user_db_id)
        saved_stats = self.db.get_calculations_by_user(user_db_id, True)

        tp_count = 0
        sl_count = 0

        profit = 0
        for stat in saved_stats:
            stat_profit = stat.profit or 0

            if stat_profit > 0:
                tp_count += round(stat_profit / stat.risk_value)
            if stat_profit < 0:
                sl_count += round(abs(stat_profit) / stat.risk_value, 1)

            profit += stat_profit

        return CalculatorStats(
            profit=profit,
            tp_count=int(tp_count),
            sl_count=round(sl_count, 1),
            all_stats_count=len(all_stats),
            saved_stats_count=len(saved_stats)
        )
