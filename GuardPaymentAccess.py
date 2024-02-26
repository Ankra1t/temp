from typing import Literal
from config_logger import logger
from telebot import types
from datetime import datetime, timedelta

from common.vars import DATE_FORMAT
from common.dt import get_datetime_now, get_str_by_datetime
from db_new import db_new
from models import User, UserInfo, Subscribe


class GuardPaymentAccess():
    """
    Класс защитник платного доступа, рассылки и бана
    """

    def __init__(self) -> None:
        self.mess = ''

    # Пробные подписки
    def set_trial(self, tg_user_id, custom_days=None, custom_tariff_id=None):
        """Дать новому пользователю тестовый период """
        if not custom_days:
            current_trial_days = int(self.get_option_trial_days())
        else:
            current_trial_days = int(custom_days)

        finish_date = get_datetime_now() + timedelta(days=current_trial_days)

        if not custom_tariff_id:
            tariff = db_new.get_first_tariff_by_product('signals')
            tariff_id = tariff.id
        else:
            tariff_id = custom_tariff_id


        subscribe = Subscribe(
            tg_user_id,
            finish_date, 1, None, 'trial', prices_id=tariff_id
        )

        # self.delete_trial(message)
        db_new.add_subsbscribe(subscribe)

        # TODO
        finish_date_show_user = get_str_by_datetime(finish_date)
        finish_date_show_admin = get_str_by_datetime(finish_date)

        return {'user': finish_date_show_user, 'admin': finish_date_show_admin}

    def set_option_trial_days(self, days):
        print(f'days ')
        print(days)
        db_new.set_option('count_trial_days_new_user', str(int(days)))

    def get_option_trial_days(self) -> int:
        days = db_new.get_option('count_trial_days_new_user')
        return days or 1

    def set_custom_paid_subscribe(self, user_id, price_id=1, count_days=1):
        """Дать пользователю платную подписку без оплаты"""
        now = get_datetime_now()
        finish_date = now + timedelta(days=count_days)

        subscribe = Subscribe(
            user_id, finish_date, 1, None, 'paid', price_id, None
        )
        db_new.add_subsbscribe(subscribe)

        # TODO
        finish_date_show_user = get_str_by_datetime(finish_date)
        finish_date_show_admin = get_str_by_datetime(finish_date)

        return {'user': finish_date_show_user, 'admin': finish_date_show_admin}

    def delete_trial(self, message: types.Message):
        """Удаление тестового период из БД"""
        db_new.del_transaction(message.from_user.id)

    def check_trial_active_by_user(self, user_id):
        """Проверить есть ли у пользователя тестовая подписка"""
        trial_subscribe = db_new.get_user_trial_subscribe(user_id)

        if trial_subscribe is None:
            return False

        trial_id = trial_subscribe.id
        active = trial_subscribe.active

        if trial_id and (active == 1):
            return trial_id
        return False

    def set_trial_subscribe_unactive_by_user(self, tg_user_id):
        """Отключить все пробные подписки у пользователя"""
        db_new.set_trial_subscribe_unactive_by_user(tg_user_id)

    # Платные подписки
    def set_paid_subscribe(self, transaction):
        """Добавить платную подписку для пользователя по результату оплаты (транзакция paid)"""
        subscribe_days = self.get_subscribe_days_prices_id(
            transaction['prices_id'])

        finish_date = get_datetime_now() + timedelta(days=subscribe_days)

        subscribe = Subscribe(
            transaction['user_id'], finish_date, 1, None, 'paid',
            transaction['prices_id'], transaction['transaction_id']
        )
        db_new.add_subsbscribe(subscribe)

        return finish_date

    def get_subscribe_days_prices_id(self, price_id):
        tariff = db_new.get_price_by_id(price_id)

        return tariff.duration_days if tariff is not None else 0

    # Получение СПИСКИ пользователей для рассылки
    def get_users_note_fin_trial(self):
        """Получаем пользователей у которых закончилась Тестовая подписка - для рассылки уведомлений"""
        return db_new.get_users_finished_subscribe('trial')

    def get_users_note_fin_paid(self):
        """Получаем платных пользователей у которых закончилась Платная подписка - для рассылки уведомлений"""
        return db_new.get_users_finished_subscribe('paid')

    def get_paid_users(self):
        """Получаем пользователей с активными подписками для платной рассылки сигналов"""
        return db_new.get_subsribed_users()

    def get_paid_more1_users(self):
        """Получаем пользователей с больше чем одной подпиской"""
        return db_new.get_subsribed_users(2)

    # Проверить может ли пользователь работать с калькулятором
    def valid_use_calc(self, user_id: int):
        user_db_id = db_new.get_user_id_by_tg_id(user_id)
        uses_count = db_new.get_calculator_uses_count(user_db_id) or 0

        # Проверять есть ли платная подписка
        if self.paid_user_product(user_id, 'calc'):
            return True

        # Проверить есть ли остаток использований калькулятора
        if uses_count > 0:
            return True

        return False

    def paid_user_product(self, user_id, product=None):
        """Проверяем оплачен ли продукт пользователем - имеется ли подписка"""
        # Проверяем текущие активные платные подписки
        subscribes = db_new.get_active_subscribes_by_user_id(user_id)

        if not subscribes:
            return False

        list_subscribes = subscribes
        now = get_datetime_now()
        for i in range(0, len(list_subscribes)):
            sub_item = list_subscribes[i]
            fin_date_subscribe_obj = sub_item.finish_dt

            if fin_date_subscribe_obj > now:
                price_item = db_new.get_price_by_id(sub_item.prices_id or 0)

                if price_item is not None and price_item.type_product == product:
                    return True
            else:
                db_new.set_deactivate_subscribe(sub_item.id)

        return False

    def get_valid_users_for_signals(self):
        """Получить пользователей для рассылки сигналов"""

        # Деактивируем подписки с просроченной датой действия
        db_new.set_unactive_subscribes('paid')
        db_new.set_unactive_subscribes('trial')

        # Получить пользователей с платной подпиской сигналы или сигналы+калькулятор
        users = db_new.get_active_subscribes_all_users()
        # print(f'кол-во len(users) {len(users)}')

        if not users:
            return None

        return users

    # # # Остальные методы
    def set_subscribe_unactive_many_users(self):
        db_new.set_unactive_subscribes('trial')

    def set_paid_subscribe_unactive_many_users(self):
        db_new.set_unactive_subscribes('paid')

    def set_subscribe_unactive(self, subscribe_id: int):
        """Убираем активность у подписки по subscribe_id """
        db_new.set_subscribe_unactive(subscribe_id)

    def set_subscribe_unactive_by_user_id(self, user_id, tariff_id = None):
        """Убираем активность у подписки для одного пользователя по user_id"""
        db_new.set_subscribe_unactive_by_user_id(user_id, tariff_id)

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

        finish_date = finish_date.strftime(DATE_FORMAT)
        db_new.set_subscribe_findate(subscribe_id or 0, finish_date)
        return finish_date

    def cancel_subscribes_for_time_type(self, time_type, count):
        """Отменить подписку за прошедший период"""
        time_start_obj = get_datetime_now()

        if time_type == 'hours':
            time_start_obj -= timedelta(hours=count)

        if time_type == 'days':
            time_start_obj -= timedelta(days=count)

        time_start = time_start_obj.strftime(DATE_FORMAT)
        time_end = get_datetime_now().strftime(DATE_FORMAT)

        logger.info(f'-----> Начало отмены дата {time_start}')
        logger.info(f'-----> Конец отмены дата {time_end}')

        db_new.set_unactive_subscribe_for_time(time_start, time_end)

        return {
            'time_start': get_str_by_datetime(time_start_obj),
            'time_end': get_str_by_datetime(get_datetime_now())
        }

    def cancel_subscribes_for_time_period(self, date_start_obj: datetime, date_end_obj: datetime):
        time_start = date_start_obj.strftime(DATE_FORMAT)
        time_end = date_end_obj.strftime(DATE_FORMAT)
        db_new.set_unactive_subscribe_for_time(time_start, time_end)

        return {
            'time_start': get_str_by_datetime(date_start_obj),
            'time_end': get_str_by_datetime(date_end_obj)
        }

        # # # # # # Вспомогательные методы
    def get_days_by_period(self, period):
        days = 1

        if period == 'week':
            days = 7
        if period == 'week2':
            days = 7*2
        if period == 'month':
            days = 30
        if period == 'month6':
            days = 30 * 6
        if period == 'year':
            days = 365
        if period == 'lifetime':
            days = 365*80

        return days