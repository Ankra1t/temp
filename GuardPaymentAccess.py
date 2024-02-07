from typing import Literal
from config_logger import logger
from telebot import types
from datetime import datetime, timedelta
from models import User, Subscribe

from db_new import db_new


class GuardPaymentAccess():
    """
    Класс защитник платного доступа, рассылки и бана

    Взаимодействие с таблицами
        pay (платежные шлюзы)
        , prices (цены, тарифы)
        , transactions (транзакции платежей)
    users (платные пользователи)
        - pay_money пополнения
        - balance текущий баланс (pay_money - потраченная сумма)
    """

    def __init__(self) -> None:
        self.mess = ''
        self.dt_format = "%Y-%m-%d %I:%M"
        self.dt_format_admin_show = "%d/%m/%Y %I:%M"
        self.dt_format_user_show = "%d/%m/%Y"

    # Тестовые подписки
    def set_trial(self, message: types.Message, custom_days = None):
        """Дать новому пользователю тестовый период """
        current_trial_days = custom_days
        if not custom_days:
            current_trial_days = self.get_option_trial_days()

        finish_date = datetime.now() + timedelta(days=current_trial_days)

        subscribe = Subscribe(
            message.from_user.id,
            finish_date, 1, None, 'trial',
        )

        # self.delete_trial(message)
        db_new.add_subsbscribe(subscribe)

        finish_date_show_user = finish_date.strftime(
            self.dt_format_user_show)
        finish_date_show_admin = finish_date.strftime(
            self.dt_format_admin_show)

        return {'user': finish_date_show_user, 'admin': finish_date_show_admin}

    def set_option_trial_days(self, days):
        print(f'days ')
        print(days)
        db_new.set_option('count_trial_days_new_user', str(int(days)))

    def get_option_trial_days(self):
        days = db_new.get_option('count_trial_days_new_user')
        return days

    def set_custom_paid_subscribe(self, user_id, count_days):
        """Дать пользователю платную подписку без оплаты"""
        now = datetime.now()
        finish_date = now + timedelta(days=count_days)

        subscribe = Subscribe(
            user_id, finish_date, 1, None, 'paid', 1, 1
        )
        db_new.add_subsbscribe(subscribe)

        finish_date_show_user = finish_date.strftime(
            self.dt_format_user_show)
        finish_date_show_admin = finish_date.strftime(
            self.dt_format_admin_show)

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

    def set_trial_subscribe_unactive_by_user(self, user_id):
        """Отключить все пробные подписки у пользователя"""
        db_new.set_trial_subscribe_unactive_by_user(user_id)

    # Платные подписки
    def set_paid_subscribe(self, transaction):
        """Добавить платную подписку для пользователя по результату оплаты (транзакция paid)"""
        subscribe_days = self.get_subscribe_days_prices_id(
            transaction['prices_id'])

        finish_date = datetime.now() + timedelta(days=subscribe_days)

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

        uses_count = db_new.get_calculator_uses_count(user_id) or 0

        # Проверять есть ли платная подписка
        if self.paid_user_product(user_id, 'calc'):
            return True

        # Проверить есть ли остаток использований калькулятора
        if uses_count > 0:
            return True
          
        return False
    
    def paid_user_product(self, user_id, product=None):
        """Проверяем оплачен ли продукт пользователем - имеется ли подписка"""
        client = db_new.get_user_by_id(user_id)

        # Проверяем текущие активные платные подписки по продукту калькулятор
        subscribes = db_new.get_active_subscribes_by_user_id(client.tg_id)

        if not subscribes:
            return False

        # Найти транзакцию по продукту
        list_subscribes = subscribes
        now = datetime.now()
        for i in range(0, len(list_subscribes)):
            sub_item = list_subscribes[i]
            fin_date_subscribe_obj = sub_item.finish_dt

            if fin_date_subscribe_obj > now:
                price_item = db_new.get_price_by_id(sub_item.prices_id)

                if price_item.type_product == product:
                    return True
            else:
                db_new.set_deactivate_subscribe(sub_item.id)

        return False

    # # # Остальные методы
    def set_subscribe_unactive_many_users(self):
        db_new.set_unactive_subscribes('trial')

    def set_paid_subscribe_unactive_many_users(self):
        db_new.set_unactive_subscribes('paid')

    def set_subscribe_unactive(self, subscribe_id: int):
        """Убираем активность у подписки по subscribe_id """
        db_new.set_subscribe_unactive(subscribe_id)

    def set_subscribe_unactive_by_user_id(self, user_id):
        """Убираем активность у подписки для одного пользователя по user_id"""
        db_new.set_subscribe_unactive_by_user_id(user_id)

    # Управление подписками
    def get_current_subscribe_user(self, user: User):
        """Получить текущую активную подписку пользователя"""
        user.subscribe = db_new.get_current_subscribe_user(user.id or 0)
        return user

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

        finish_date = finish_date.strftime(self.dt_format)
        db_new.set_subscribe_findate(subscribe_id or 0, finish_date)
        return finish_date

    def cancel_subscribes_for_time_type(self, time_type, count):
        """Отменить подписку за прошедший период"""
        time_start_obj = datetime.now()

        if time_type == 'hours':
            time_start_obj -= timedelta(hours=count)

        if time_type == 'days':
            time_start_obj -= timedelta(days=count)

        time_start = time_start_obj.strftime(self.dt_format)
        time_end = datetime.now().strftime(self.dt_format)

        logger.info(f'-----> Начало отмены дата {time_start}')
        logger.info(f'-----> Конец отмены дата {time_end}')

        db_new.set_unactive_subscribe_for_time(time_start, time_end)

        return {
            'time_start': time_start_obj.strftime(self.dt_format_admin_show),
            'time_end': datetime.now().strftime(self.dt_format_admin_show)
        }

    def cancel_subscribes_for_time_period(self, date_start_obj: datetime, date_end_obj: datetime):
        time_start = date_start_obj.strftime(self.dt_format)
        time_end = date_end_obj.strftime(self.dt_format)
        db_new.set_unactive_subscribe_for_time(time_start, time_end)

        return {
            'time_start': date_start_obj.strftime(self.dt_format_admin_show),
            'time_end': date_end_obj.strftime(self.dt_format_admin_show)
        }
