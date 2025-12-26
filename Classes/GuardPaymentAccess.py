from typing import Optional
from datetime import timedelta

from common.dt import get_datetime_now

from db import db
from models import Subscribe, Transactions, PRODUCT_TYPE


class GuardPaymentAccess():
    """
    Класс защитник платного доступа, рассылки и бана
    """

    def __init__(self) -> None:
        pass

    # Пробные подписки
    def set_trial(self, user_db_id: int, product: PRODUCT_TYPE, custom_days: Optional[int] = None):
        """Дать новому пользователю тестовый период """
        trial_days = custom_days or self.get_option_trial_days()

        finish_date = get_datetime_now() + timedelta(days=trial_days)

        subscribe = Subscribe(
            id=-1,
            user_id=user_db_id,
            finish_dt=finish_date,
            product_type=product,
            active=True,
        )

        db.add_subscribe(subscribe)

        return finish_date

    def set_option_trial_days(self, days: int):
        db.set_option('count_trial_days_new_user', str(days))

    def get_option_trial_days(self) -> int:
        default = 1
        try:
            days = int(db.get_option('count_trial_days_new_user') or default)
        except:
            days = default

        return days

    def deactivate_user_trial_subscribe(self, user_db_id: int):
        """Отключить все пробные подписки у пользователя"""
        db.set_trial_subscribe_unactive_by_user(user_db_id)

    # Платные подписки
    def set_paid_subscribe(self, transaction: Transactions):
        """Добавить платную подписку для пользователя по результату оплаты (транзакция PAID)"""
        subscribe_days = transaction.duration_days

        finish_date = get_datetime_now() + timedelta(days=subscribe_days)

        subscribe = Subscribe(
            id=-1,
            user_id=transaction.user_id,
            finish_dt=finish_date,
            product_type=transaction.type_product,
            transactions_payed_id=transaction.id,
            active=True,
        )

        db.add_subscribe(subscribe)

        return finish_date

    def set_subscribe_unactive_by_user_id(self, tg_id: int):
        user_db_id = db.get_user_id_by_tg_id(tg_id)
        db.set_subscribe_unactive_by_user_id(user_db_id)

    def get_days_by_period(self, period):
        days = 1

        if period == 'week':
            days = 7
        if period == 'week2':
            days = 7 * 2
        if period == 'month':
            days = 30
        if period == 'month6':
            days = 30 * 6
        if period == 'year':
            days = 365
        if period == 'lifetime':
            days = 365 * 80

        return days
