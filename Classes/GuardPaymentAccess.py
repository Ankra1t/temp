from typing import Literal, Optional
from datetime import datetime, timedelta

from common.dt import get_datetime_now, get_str_by_datetime

from db import db
from models import User, Subscribe, Transactions, PRODUCT_TYPE


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

        db.add_subsbscribe(subscribe)

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
        """Добавить платную подписку для пользователя по результату оплаты (транзакция paid)"""
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

        db.add_subsbscribe(subscribe)

        return finish_date

    # Получение СПИСКИ пользователей для рассылки
    def get_users_note_fin_trial(self):
        """Получаем пользователей у которых закончилась Тестовая подписка - для рассылки уведомлений"""
        return db.get_users_finished_subscribe('trial')

    def get_users_note_fin_paid(self):
        """Получаем платных пользователей у которых закончилась Платная подписка - для рассылки уведомлений"""
        return db.get_users_finished_subscribe('paid')

    def get_paid_users(self):
        """Получаем пользователей с активными подписками для платной рассылки рекомендаций"""
        return db.get_subsribed_users()

    def get_paid_more1_users(self):
        """Получаем пользователей с больше чем одной подпиской"""
        return db.get_subsribed_users(2)

    # Проверить может ли пользователь работать с калькулятором
    def valid_use_calc(self, tg_id: int):
        user_db_id = db.get_user_id_by_tg_id(tg_id)

        freeze_dt = db.get_user_calc_freeze(user_db_id)

        uses_count = db.get_calculator_uses_count(user_db_id) or 0
        is_sub = self.paid_user_product(tg_id, 'calc')
        valid_use = uses_count > 0 or is_sub

        if freeze_dt is not None and (freeze_dt < get_datetime_now() or not valid_use):
            db.set_user_calc_freeze(user_db_id, None)
            freeze_dt = None

        # Проверка на заморозку
        if freeze_dt is not None:
            return False

        # Проверять есть ли платная подписка или остаток использований калькулятора
        if valid_use:
            return True

        return False

    def paid_user_product(self, tg_id, product=None):
        """Проверяем оплачен ли продукт пользователем - имеется ли подписка"""
        user_db_id = db.get_user_id_by_tg_id(tg_id)
        subscribes = db.get_active_subscribes_by_user_id(user_db_id)

        if not subscribes:
            return False

        list_subscribes = subscribes
        now = get_datetime_now()
        for i in range(0, len(list_subscribes)):
            sub_item = list_subscribes[i]
            fin_date_subscribe_obj = sub_item.finish_dt

            if fin_date_subscribe_obj > now:
                if sub_item.product_type == product or sub_item.product_type == 'trial':
                    return True
            else:
                db.deactivate_subscribe(sub_item.id or 0)

        return False

    def get_valid_users_for_signals(self):
        """Получить пользователей для рассылки рекомендаций"""

        # Деактивируем подписки с просроченной датой действия
        db.check_unactive_subscribes('paid')
        db.check_unactive_subscribes('trial')

        # Получить пользователей с платной подпиской рекомендации или рекомендации+калькулятор
        users = db.get_active_subscribes_all_users(False)
        # print(f'кол-во len(users) {len(users)}')

        if not users:
            return None

        return users

    # # # Остальные методы
    def set_subscribe_unactive_many_users(self):
        db.check_unactive_subscribes('trial')

    def set_paid_subscribe_unactive_many_users(self):
        db.check_unactive_subscribes('paid')

    def set_subscribe_unactive(self, subscribe_id: int):
        """Убираем активность у подписки по subscribe_id """
        db.set_subscribe_unactive(subscribe_id)

    def set_subscribe_unactive_by_user_id(self, tg_id: int):
        user_db_id = db.get_user_id_by_tg_id(tg_id)
        db.set_subscribe_unactive_by_user_id(user_db_id)

    def update_user_subscribe_findate(self, user: User, direct: Literal['add', 'deduct']):
        if user.subscribe is None:
            return

        subscribe_id = user.subscribe.id
        current_date = user.subscribe.finish_dt
        days: int = user.subscribe_days or 0

        current_date_obj = current_date

        if direct == 'add':
            finish_date = current_date_obj + timedelta(days=int(days))
        else:
            finish_date = current_date_obj - timedelta(days=int(days))

        db.set_subscribe_findate(subscribe_id or 0, finish_date)
        return finish_date

    def cancel_subscribes_for_time_type(self, time_type, count):
        """Отменить подписку за прошедший период"""
        time_start = get_datetime_now()
        time_end = get_datetime_now()

        if time_type == 'hours':
            time_start -= timedelta(hours=count)

        if time_type == 'days':
            time_start -= timedelta(days=count)

        db.set_unactive_subscribe_for_time(time_start, time_end)

        return {
            'time_start': get_str_by_datetime(time_start),
            'time_end': get_str_by_datetime(time_end)
        }

    def cancel_subscribes_for_time_period(self, time_start: datetime, time_end: datetime):
        db.set_unactive_subscribe_for_time(time_start, time_end)

        return {
            'time_start': get_str_by_datetime(time_start),
            'time_end': get_str_by_datetime(time_end)
        }

        # # # # # # Вспомогательные методы
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
