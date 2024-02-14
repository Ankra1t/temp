from datetime import datetime
from typing import Any, Literal, Optional
import psycopg2
from psycopg2.extras import DictCursor, DictRow

from common.vars import DATE_FORMAT
from config_global import DB_PG_HOST, DB_PG_NAME, DB_PG_PASS, DB_PG_PORT, DB_PG_USER
from models import Forex, Future, Post, PostDetails, Text, UserInfo, Price, Subscribe, Transactions, Purchase, Worker, Client


SUBSCRIBE_TYPE = Literal['trial', 'paid']
PRODUCT_TYPE = Literal['signals', 'calc', 'calc_signals']
BASE_VALUE_TYPE = Literal['base_deposit', 'base_risk_percent', 'base_currency']
FILTER_TYPE = Literal['by_date_new', 'by_date_old', 'by_paid']

LANGUAGES_TYPE = Literal['ru', 'en']
LANGUAGES: tuple[LANGUAGES_TYPE, ...] = ('ru', 'en')
MARKETS_TYPE = Literal['crypto', 'future', 'paper', 'forex']


class Database:
    def __init__(self, user: str, password: str, host: str, port: int, database: str):
        try:
            self.connection = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            self.curs = self.connection.cursor(cursor_factory=DictCursor)
        except Exception as error:
            print(f"Ошибка при работе с PostgreSQL: {error}")

    # # # # # # # #  Prices
    def _data_to_price(self, data: DictRow):
        return Price(
            data.get('name'),
            data.get('duration_days'),
            data.get('price'),
            data.get('currency'),
            data.get('id'),
            data.get('img'),
            data.get('description'),
            data.get('discount_percent'),
            data.get('discount_findate'),
            data.get('type_product'),
            data.get('switch_active'),
            data.get('price_findate'),
        )

    def get_prices(self, active: int=1, switch_active = 1) -> list[Price]:
        """Получение тарифа"""
        if not switch_active:
            query = """SELECT * FROM prices WHERE active = %s"""
            params = (active, )
        else:
            query = """SELECT * FROM prices WHERE active = %s AND switch_active = %s"""
            params = (active, switch_active, )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_price(el), data))
        except Exception as e:
            print(f'ERROR[get_prices]: {e}')
            self.connection.rollback()
            return []

    def get_prices_by_product(self, product_id, active: int, switch_active = 1) -> list[Price]:
        """Получение тарифа по типу продукта"""
        if not switch_active:
            query = """SELECT * FROM prices WHERE active = %s AND type_product = %s"""
            params = (active, product_id, )
        else:
            query = """SELECT * FROM prices WHERE active = %s AND type_product = %s AND switch_active = %s"""
            params = (active, product_id, switch_active,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_price(el), data))
        except Exception as e:
            print(f'ERROR[get_prices_by_product]: {e}')
            self.connection.rollback()
            return []

    def get_price_by_id(self, id: int, switch_active = 1):
        if not switch_active:
            query = "SELECT * FROM prices WHERE id = %s"
            params = (id,)
        else:
            query = "SELECT * FROM prices WHERE id = %s AND switch_active = %s"
            params = (id, switch_active,)
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            if data is None:
                return None
            return self._data_to_price(data)
        except Exception as e:
            print(f'ERROR[get_price_by_id]: {e}')
            self.connection.rollback()
            return None

    def get_price_by_name(self, name: str, switch_active = 1):
        """Получение цены по имени"""
        query = "SELECT * FROM prices WHERE name = %s AND switch_active = %s"
        params = (name, switch_active, )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            if data is None:
                return None

            return self._data_to_price(data)
        except Exception as e:
            print(f'ERROR[get_prices_by_name]: {e}')
            self.connection.rollback()
            return None

    def update_price(self, name: str, price: float):
        """Обновить цену"""
        datetime_now = datetime.utcnow()
        query = "UPDATE prices set price = %s, updated_at = %s WHERE name = %s"
        params = (price, datetime_now, name)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price]: {e}')
            self.connection.rollback()
            return False

    def update_price_field(self, field, value, price_id: int):
        """Обновить цену"""
        datetime_now = datetime.utcnow()
        query = f"UPDATE prices set {field} = %s, updated_at = %s WHERE id = %s"
        params = (value, datetime_now, price_id, )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price]: {e}')
            self.connection.rollback()
            return False

    def add_price(self, data: Price):
        """Добавление цены"""
        datetime_now = datetime.utcnow()
        query = ("INSERT INTO prices "
                 "(name, currency, price, description, img, duration_days, type_product, "
                 "updated_at, created_at) "
                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        params = (data.name, data.currency, data.price, data.description,
                  data.img, data.duration_days, data.type_product,
                  datetime_now, datetime_now)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f'ERROR[add_price]: {e}')
            self.connection.rollback()

    def deactive_price(self, id: int):
        """Установить цену не активной"""
        datetime_now = datetime.utcnow()
        query = "UPDATE prices set active = 0, updated_at = %s WHERE id = %s"
        params = (datetime_now, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[deactive_price]: {e}')
            self.connection.rollback()
            return False

    def set_price_discount(self, id: int, percent: float, fin_date: datetime):
        """Установка скидки тарифу"""
        datetime_now = datetime.utcnow()
        query = "UPDATE prices set discount_percent = %s, discount_findate = %s, updated_at = %s WHERE id = %s"
        params = (percent, fin_date, datetime_now, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_price_discount]: {e}')
            self.connection.rollback()
            return False

    # # # # # # # # Subscribes # # # # # # # #
    def _data_to_subsbscribe(self, data: DictRow):
        return Subscribe(
            data.get('tg_user_id'),
            data.get('finish_dt'),
            data.get('active'),
            data.get('id'),
            data.get('subscribe_type'),
            data.get('prices_id'),
            data.get('transactions_payed_id'),
        )

    def add_subsbscribe(self, sub: Subscribe):
        query = ("INSERT INTO "
                 "subscribes (tg_user_id, finish_dt, "
                 "subscribe_type, active, prices_id, transactions_payed_id) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")
        params = (sub.tg_user_id, sub.finish_dt, sub.type, sub.active,
                  sub.prices_id, sub.transactions_payed_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_subsbscribe]: {e}')
            self.connection.rollback()
            return False

    def get_current_subscribe_user(self, user_id: int):
        query = 'SELECT * FROM subscribes WHERE tg_user_id = %s AND active = 1'
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if data is None else self._data_to_subsbscribe(data)
        except Exception as e:
            print(f'ERROR[get_current_subscribe_user]: {e}')
            self.connection.rollback()
            return None

    def get_user_trial_subscribe(self, user_id: int):
        query = "SELECT * FROM subscribes WHERE tg_user_id = %s AND subscribe_type = %s"
        params = (user_id, 'trial')

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()

            return data if (data is None) else self._data_to_subsbscribe(data)
        except Exception as e:
            print(f'ERROR[get_user_trial_subscribe]: {e}')
            self.connection.rollback()
            return None

    # TODO - продумать данные функция работы с получнием пользователей с подпиской и без
    def get_users_finished_subscribe(self, type: SUBSCRIBE_TYPE) -> list[DictRow]:
        datetime_now = datetime.utcnow()
        query = (
            'SELECT u.id, u.created_at, u.username, u.count_sub, u.count_days, '
            'u.refer, u.pay_money, u.balance, u.count_les, u.id, u.ban, sub.finish_dt '
            'FROM subscribes AS sub, users AS u WHERE sub.finish_dt < %s '
            'AND sub.subscribe_type = %s AND sub.active = %s AND sub.tg_user_id = u.id'
        )
        params = (datetime_now, type, 1)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return data
            # return list(map(lambda el: self._data_to_subsbscribe(el), data))
        except Exception as e:
            print(f'ERROR[get_users_finished_subscribe]: {e}')
            self.connection.rollback()
            return []

    def set_subscribe_unactive_by_user_id(self, user_id: int):
        datetime_now = datetime.utcnow()
        query = "UPDATE subscribes set active = %s, updated_at = %s WHERE tg_user_id = %s"
        params = (0, datetime_now, user_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_subscribe_unactive_by_user_id]: {e}')
            self.connection.rollback()
            return False

    def set_subscribe_unactive(self, subscribe_id: int):
        datetime_now = datetime.utcnow()
        query = "UPDATE subscribes set active = %s, updated_at = %s WHERE id = %s"
        params = (0, datetime_now, subscribe_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_subscribe_unactive]: {e}')
            self.connection.rollback()
            return False

    def set_trial_subscribe_unactive_by_user(self, user_id):
        datetime_now = datetime.now().strftime(DATE_FORMAT)
        query = "UPDATE subscribes set active = %s, updated_at = %s WHERE tg_user_id = %s AND subscribe_type = %s"
        params = (0, datetime_now, user_id, 'trial')

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_trial_subscribe_unactive_by_user]: {e}')
            self.connection.rollback()
            return False

    def set_subscribe_findate(self, subscribe_id: int, finish_date: str):
        datetime_now = datetime.utcnow()
        query = "UPDATE subscribes set finish_dt = %s, updated_at = %s WHERE id = %s"
        params = (finish_date, datetime_now, subscribe_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_subscribe_findate]: {e}')
            self.connection.rollback()
            return False

    def set_deactivate_subscribe(self, subscribe_id):
        datetime_now = datetime.utcnow()
        query = (
            'UPDATE subscribes set active = %s, updated_at = %s '
            'WHERE id = %s'
        )
        params = (0, datetime_now, subscribe_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_deactivate_subscribe]: {e}')
            self.connection.rollback()
            return False

    def set_unactive_subscribes(self, type: SUBSCRIBE_TYPE):
        datetime_now = datetime.utcnow()
        query = (
            'UPDATE subscribes set active = %s, updated_at = %s '
            'WHERE finish_dt < %s AND subscribe_type = %s'
        )
        params = (0, datetime_now, datetime_now, type, )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_unactive_subscribes]: {e}')
            self.connection.rollback()
            return False

    def set_unactive_subscribe_for_time(self, time_start: str, time_end: str):
        datetime_now = datetime.utcnow()
        query = (
            "UPDATE subscribes set active = %s, updated_at = %s "
            "WHERE (updated_at BETWEEN %s AND %s ) AND active = %s"
        )
        params = (0, datetime_now, time_start, time_end, 1,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_unactive_trial_subscribes]: {e}')
            return False

    def get_active_subscribes_by_user_id(self, user_id):
        query = 'SELECT * FROM subscribes WHERE tg_user_id = %s AND active = 1'
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_subsbscribe(el), data))

        except Exception as e:
            print(f'ERROR[get_active_subscribes_by_user_id]: {e}')
            self.connection.rollback()
            return None

    def get_active_subscribes_all_users(self, ban: int = 0):
        """Получить активные подписки для всех пользователей"""
        query = (
            'SELECT u.id AS id, u.username_tg AS username, u.id_telegram AS tg_id, '
            'p.type_product AS type_product, '
            'sub.id AS sub_id, '
            'sub.finish_dt AS sub_finish, '
            'ub.refer_id AS refer, u.ban AS ban, u.created_at AS created_at '
            'FROM subscribes sub, users u, prices p, tgbotusers ub '
            'WHERE '
            '(sub.subscribe_type = %s OR sub.subscribe_type = %s) '
            'AND sub.active = %s AND sub.tg_user_id = u.id_telegram '
            'AND sub.prices_id = p.id '
            'AND ub.user_id = u.id '
            'AND u.ban = %s '
        )
        params = ('paid', 'trial', 1, ban)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return data
            # return list(map(lambda el: self._data_to_subsbscribe(el), data))
        except Exception as e:
            print(f'ERROR[get_users_finished_subscribe]: {e}')
            self.connection.rollback()
            return []

        pass

    def _data_to_client(self, data: DictRow):
        return Client(
            user=UserInfo(
                data.get('user_id')
            ),
            subscribes=Subscribe(

            )
        )

    def switch_tariff(self, tariff_id: int, switch_active: int):
        """Включить или выключить тариф"""
        datetime_now = datetime.utcnow()
        query = "UPDATE prices set switch_active = %s, updated_at = %s WHERE id = %s"
        params = (switch_active, datetime_now, tariff_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[switch_tariff]: {e}')
            self.connection.rollback()
            return False

    def check_switch_tariff(self, tariff_id: int):
        query = "SELECT switch_active FROM prices WHERE id = %s"
        params = (tariff_id, )
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data[0] if (data is not None) else 0
        except Exception as e:
            print(f'ERROR[check_switch_tariff]: {e}')
            self.connection.rollback()
            return None

    def set_findate_tariff(self, tariff_id: int, date):
        """Установить дату окончания тарифа"""
        datetime_now = datetime.utcnow()
        query = "UPDATE prices set price_findate = %s, updated_at = %s WHERE id = %s"
        params = (date, datetime_now, tariff_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_findate_tariff]: {e}')
            self.connection.rollback()
            return False

    def switch_off_finish_tariffs(self, today: str):
        """Установить дату окончания тарифа"""
        datetime_now = datetime.utcnow()
        query = "UPDATE prices set switch_active = %s, updated_at = %s WHERE price_findate < %s"
        switch = 0
        params = (switch, datetime_now, today)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[switch_off_finish_tariffs]: {e}')
            self.connection.rollback()
            return False

    # # # # # # # #  Transactions
    def _data_to_transaction(self, data: DictRow):
        return Transactions(
            data.get('user_id'),
            data.get('id'),
            data.get('code'),
            data.get('link'),
            data.get('sum'),
            data.get('currency'),
            data.get('price_id'),
            data.get('status'),
            data.get('payment_date'),
        )

    def add_transaction(self, trans: Transactions):

        query = (
            "INSERT INTO transactions"
            "(user_id, code, link, sum, currency, price_id, status) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (trans.user_id, trans.code, trans.link, trans.sum,
                  trans.currency, trans.price_id, trans.status)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_transaction]: {e}')
            self.connection.rollback()
            return False

    def get_wait_transaction(self, code: str, status: str):
        query = (
            "SELECT id, user_id, price_id, sum FROM transactions "
            "WHERE code = %s AND status = %s"
        )
        params = (code, status)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if data is None else self._data_to_transaction(data)
        except Exception as e:
            print(f'ERROR[get_wait_transaction]: {e}')
            self.connection.rollback()
            return None

    def get_paid_transactions_by_user(self, user_id: int):
        """Получить платные транзакции пользователя"""
        query = ("SELECT * FROM transactions "
                 "WHERE user_id = %s AND status = %s"
                 )
        status = 'paid'
        params = (user_id, status, )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_transaction(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_by_user]: {e}')
            self.connection.rollback()
            return []

    def get_paid_transactions_all(self):
        """Получить все оплаченные транзакции"""
        query = ("SELECT * FROM transactions "
                 "WHERE status = %s"
                 )
        status = 'paid'
        params = (status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_transaction(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_all]: {e}')
            self.connection.rollback()
            return []

    def get_paid_transactions_period(self, start_date, fin_date):
        """Получить все оплаченные транзакции"""
        query = ("SELECT * FROM transactions "
                 "WHERE (payment_date BETWEEN %s AND %s ) "
                 "AND status = %s "
                 )
        status = 'paid'
        params = (start_date, fin_date, status, )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_transaction(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_all]: {e}')
            self.connection.rollback()
            return []

    def get_paid_transactions_product(self, product):
        """Получить все оплаченные транзакции по продукту"""
        query = ("SELECT * "
                 "FROM transactions t, prices p  "
                 "WHERE t.price_id = p.id AND p.type_product = %s "
                 "AND status = %s "
                 )
        status = 'paid'
        params = (product, status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_transaction(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_product]: {e}')
            self.connection.rollback()
            return []

    def get_paid_transactions_summ(self):
        """Суммы по транзакциям"""
        query = ("SELECT sum(sum) FROM transactions "
                 "WHERE status = %s"
                 )
        status = 'paid'
        params = (status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data[0] if (data is not None) else 0
        except Exception as e:
            print(f'ERROR[get_paid_transactions_summ]: {e}')
            self.connection.rollback()
            return []

    def get_paid_transactions_summ_period(self, start_date, fin_date):
        """Суммы по транзакциям за период"""
        query = ("SELECT sum(sum) FROM transactions "
                 "WHERE (payment_date BETWEEN %s AND %s ) "
                 "AND status = %s "
                 )
        status = 'paid'
        params = (start_date, fin_date, status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data[0] if (data is not None) else 0
        except Exception as e:
            print(f'ERROR[get_paid_transactions_summ_period]: {e}')
            self.connection.rollback()
            return []

    def get_paid_transactions_summ_product(self, product):
        """Суммы по транзакциям по продукту"""
        query = ("SELECT sum(sum) "
                 "FROM transactions t, prices p "
                 "WHERE t.price_id = p.id AND p.type_product = %s "
                 "AND status = %s "
                 )
        status = 'paid'
        params = (product, status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data[0] if (data is not None) else 0
        except Exception as e:
            print(f'ERROR[get_paid_transactions_summ_product]: {e}')
            self.connection.rollback()
            return []


    def get_purchases_by_user(self, user_id: int):
        """Получение покупок пользователя"""
        query = ("SELECT t.user_id, p.id AS price_id, p.name AS price_name, p.type_product AS product, "
                 "t.sum AS real_sum, p.price AS tariff_price, "
                 "t.currency AS currency, p.duration_days AS duration, t.payment_date AS date, "
                 "t.created_at AS create_date "
                 "FROM transactions t, prices p "
                 "WHERE "
                 "t.user_id = %s AND t.status = %s "
                 "AND t.price_id = p.id"
                 )
        status = 'paid'
        params = (user_id, status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            # return data
            return list(map(lambda el: self._data_to_purchase(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_by_user]: {e}')
            self.connection.rollback()
            return []

    def _data_to_purchase(self, data: DictRow):
        return Purchase(
            data.get('user_id'),
            data.get('price_id'),
            data.get('price_name'),
            data.get('product'),
            data.get('real_sum'),
            data.get('tariff_price'),
            data.get('currency'),
            data.get('duration'),
            data.get('date'),
            data.get('create_date'),
        )

    def get_purchases_all_users(self):
        query = ("SELECT t.user_id, p.id AS price_id, p.name AS price_name, p.type_product AS product, "
                 "t.sum AS real_sum, p.price AS tariff_price, "
                 "t.currency AS currency, p.duration_days AS duration, t.payment_date AS date, "
                 "t.created_at AS create_date "
                 "FROM transactions t, prices p "
                 "WHERE "
                 "t.status = %s "
                 "AND t.price_id = p.id"
                 )
        status = 'paid'
        params = (status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            # return data
            return list(map(lambda el: self._data_to_purchase(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_by_user]: {e}')
            self.connection.rollback()
            return []

    def set_transactions_complete(self, id: int):
        datetime_now = datetime.utcnow()
        query = "UPDATE transactions set status = %s, payment_date = %s WHERE id = %s"
        params = ('paid', datetime_now, id, )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_transactions_complete]: {e}')
            self.connection.rollback()
            return False

    def del_transaction(self, user_id: int):
        """Deprecated: транзакции удалять нельзя"""
        query = "DELETE FROM transactions WHERE user_id = %s"
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[del_transaction]: {e}')
            self.connection.rollback()
            return False

    # # # # # # # #  Users
    def _data_to_user(self, data: DictRow):
        return UserInfo(
            id=data.get('id'),
            tg_id=data.get('id_telegram'),
            username=data.get('username_tg') or '',
            refer=data.get('refer_id') or -1,
            ban=data.get('ban') or 0,
            registration_dt=data.get('created_at') or datetime(2023, 5, 5)
        )

    USER_INFO_QUERY = (
        'SELECT u.id, u.id_telegram, u.username_tg, tu.refer_id, u.ban, u.created_at  '
        'FROM users as u LEFT JOIN tgbotusers as tu ON u.id = tu.user_id '
    )

    def get_all_users(self) -> list[UserInfo]:
        query = self.USER_INFO_QUERY

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda u: self._data_to_user(u), data))
        except Exception as e:
            print(f'ERROR[get_all_users]: {e}')
            self.connection.rollback()
            return []

    def check_tg_user_tables(self, id: int):
        query = 'SELECT * FROM tgbotusers WHERE user_id = %s'
        query2 = 'SELECT * FROM tgcalc_user_settings WHERE user_id = %s'
        params = id,

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            self.curs.execute(query2, params)
            data2 = self.curs.fetchone()

            if (data is None) or (data2 is None):
                return False
            else:
                return True
        except Exception as e:
            print(f'ERROR [check_tg_user_tables]: {e}')
            self.connection.rollback()
            return False

    def create_tg_user_tables(self, id: int):
        query = 'INSERT INTO tgbotusers (user_id) VALUES (%s)'
        query2 = 'INSERT INTO tgcalc_user_settings (user_id) VALUES (%s)'
        params = id,

        try:
            self.curs.execute(query, params)
            self.curs.execute(query2, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR [create_tg_user_tables]: {e}')
            self.connection.rollback()
            return False

    def get_paginated_users(self, limit=10, page=1, filter: FILTER_TYPE = 'by_date_new') -> list[UserInfo]:
        """Получить постраничный список пользователей"""
        query = self.USER_INFO_QUERY

        if filter == 'by_paid':
            query += 'LEFT JOIN (SELECT tg_user_id, active, max(finish_dt) as finish_dt FROM subscribes '
            query += 'WHERE active = 1 GROUP BY tg_user_id, active) sub on u.id_telegram = sub.tg_user_id '
            query += 'ORDER BY sub.active ASC, sub.finish_dt DESC '
        else:
            query += f"ORDER BY u.created_at {'ASC' if filter == 'by_date_old' else 'DESC'}, u.id ASC "

        query += "LIMIT %s OFFSET %s "

        params = (limit, (page - 1) * limit)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data))
        except Exception as e:
            print(f'ERROR[get_paginated_users]: {e}')
            self.connection.rollback()
            return []

    def get_banned_users(self) -> list[UserInfo]:
        query = self.USER_INFO_QUERY + 'WHERE u.ban = 1'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda u: self._data_to_user(u), data))
        except Exception as e:
            print(f'ERROR[get_banned_users]: {e}')
            self.connection.rollback()
            return []

    def get_subsribed_users(self, min_sub_count=1) -> list[UserInfo]:
        query = self.USER_INFO_QUERY + (
            'WHERE u.ban = 0 '
            f'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram) >= {min_sub_count} '
            'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram AND sub.active = 1) > 0 '
        )

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_subsribed_users]: {e}')
            self.connection.rollback()
            return []

    def get_not_subscribed_users(self) -> list[UserInfo]:
        query = self.USER_INFO_QUERY + (
            'WHERE u.ban = 0 '
            'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram AND sub.active = 1) = 0 '
        )

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_not_subscribed_users]: {e}')
            self.connection.rollback()
            return []

    def get_users_count(self):
        try:
            self.curs.execute("SELECT * FROM users")
            return len(self.curs.fetchall())
        except Exception as e:
            print(f'ERROR[get_users_count]: {e}')
            self.connection.rollback()
            return 0

    def get_user_id_by_tg_name(self, username: str):
        """Получение пользователя по имени"""
        query = 'SELECT id FROM users WHERE username_tg = %s'
        params = (username,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return int(data.get('id')) if (data is not None) else 0
        except Exception as e:
            print(f'ERROR[get_user_id_by_tg_name]: {e}')
            self.connection.rollback()
            return 0

    def get_user_id_by_tg_id(self, tg_id: int):
        """Получение пользователя по id телеграм"""
        query = 'SELECT id FROM users WHERE id_telegram = %s'
        params = (tg_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return int(data.get('id')) if (data is not None) else 0
        except Exception as e:
            print(f'ERROR[get_user_id_by_tg_id]: {e}')
            self.connection.rollback()
            return 0

    def get_user_referals(self, id: int) -> list[UserInfo]:
        """Получить рефералов юзера"""
        query = self.USER_INFO_QUERY + 'WHERE tu.refer_id = %s'
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data))
        except Exception as e:
            print(f'ERROR[get_user_referals]: {e}')
            self.connection.rollback()
            return []

    def get_user_by_id(self, id: int):
        """Получение пользователя"""
        query = self.USER_INFO_QUERY + 'WHERE u.id = %s'
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_user(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_user_by_id]: {e}')
            self.connection.rollback()
            return None

    def get_user_by_tg_id(self, tg_id: int):
        """Получение пользователя"""
        query = self.USER_INFO_QUERY + 'WHERE u.id_telegram = %s'
        params = (tg_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_user(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_user_by_id]: {e}')
            self.connection.rollback()
            return None

    # Users - Lessons
    def add_lesson_count(self, id: int):
        query = "UPDATE tgbotusers set lesson_count = %s WHERE user_id = %s"
        count = self.get_lesson_count(id) + 1
        params = (count, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_lesson_count]: {e}')
            self.connection.rollback()
            return False

    def get_lesson_count(self, id: int):
        query = "SELECT lesson_count FROM tgbotusers WHERE user_id = %s"
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()

            if data == None:
                return 1
            else:
                return data['lesson_count']
        except Exception as e:
            print(f'ERROR[get_lesson_count]: {e}')
            self.connection.rollback()
            return 1

    # Users - Ban
    def check_ban_user(self, id: int):
        """Проверка на бан"""
        query = "SELECT ban FROM users WHERE id = %s"
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data == 1
        except Exception as e:
            print(f'ERROR[check_ban_user]: {e}')
            self.connection.rollback()
            return False

    def set_user_ban(self, id: int, ban: int):
        query = 'UPDATE users set ban = %s WHERE id = %s'
        params = (ban, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_ban]: {e}')
            self.connection.rollback()
            return False

    # Users - Settings
    def get_user_base(self, id: int) -> dict[BASE_VALUE_TYPE, Any]:
        """Получить значения для автозаполнения пользователя"""
        query = (
            'SELECT base_deposit, base_risk_percent, base_currency FROM tgcalc_user_settings '
            'WHERE user_id = %s'
        )
        params = (id,)
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return {
                'base_deposit': None if (data is None) else data.get('base_deposit'),
                'base_risk_percent': None if (data is None) else data.get('base_risk_percent'),
                'base_currency': None if (data is None) else data.get('base_currency')
            }
        except Exception as e:
            print(f'ERROR[get_user_base]: {e}')
            self.connection.rollback()
            return {
                'base_deposit': None,
                'base_risk_percent': None,
                'base_currency': None
            }

    def set_user_base(self, user_id: int, type: BASE_VALUE_TYPE, value: float):
        """Установить значения для автозаполения пользователя"""
        value = round(value, 2)
        query = f'UPDATE tgcalc_user_settings SET {type} = %s WHERE user_id = %s'
        params = (value, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_base]: {e}')
            self.connection.rollback()
            return False

    def set_user_currency(self, user_id: int, value: str):
        """Установить значения для автозаполения пользователя"""
        query = 'UPDATE tgcalc_user_settings SET base_currency = %s WHERE user_id = %s'
        params = (value, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_currency]: {e}')
            self.connection.rollback()
            return False

    def get_user_risk_is_percent(self, user_id: int) -> bool:
        query = 'SELECT risk_is_percent FROM tgcalc_user_settings WHERE user_id = %s'
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()

            if data is not None and data.get('risk_is_percent') == 1:
                return True
            else:
                return False
        except Exception as e:
            print(f'ERROR[get_user_risk_is_percent]: {e}')
            self.connection.rollback()
            return False

    def set_user_risk_is_percent(self, user_id: int, value: bool):
        query = 'UPDATE tgcalc_user_settings SET risk_is_percent = %s WHERE user_id = %s'
        params = (int(value), user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_risk_is_percent]: {e}')
            self.connection.rollback()
            return False

    def get_user_lang(self, user_id: int) -> Optional[LANGUAGES_TYPE]:
        """Получить язык пользователя"""
        query = 'SELECT lang FROM users WHERE id = %s'
        params = (user_id,)
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if (data is None) else data.get('lang')
        except Exception as e:
            print(f'ERROR[get_user_lang]: {e}')
            self.connection.rollback()
            return None

    def set_user_lang(self, user_id: int, lang: LANGUAGES_TYPE):
        """Установить язык пользователя"""
        if len(lang) > 5:
            return False

        query = "UPDATE users SET lang = %s WHERE id = %s"
        params = (lang, user_id)
        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_lang]: {e}')
            self.connection.rollback()
            return False

    def get_calculator_users_id(self) -> list[int]:
        """Получить всех пользователей Калькулятора Бота"""
        query = 'SELECT user_id FROM tgcalc_user_settings'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return [] if (data is None) else list(map(lambda el: el['user_id'], data))
        except Exception as e:
            print(f'ERROR[get_calculator_users_id]: {e}')
            self.connection.rollback()
            return []

    def delete_calculator_user(self, user_id: int):
        """Удалить пользователя из калькулятора"""
        query = "DELETE FROM tgcalc_user_settings WHERE user_id = %s"
        params = (user_id,)
        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[delete_calculator_user]: {e}')
            self.connection.rollback()
            return False

    def get_calculator_uses_count(self, user_id: int) -> int | None:
        """Получить количество использований калькулятора пользователем"""
        query = 'SELECT uses_count FROM tgcalc_user_settings WHERE user_id = %s'
        params = (user_id,)
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if (data is None) else data.get('uses_count')
        except Exception as e:
            print(f'ERROR[get_calculator_uses_count]: {e}')
            self.connection.rollback()
            return None

    def minus_calculator_uses_count(self, user_id: int):
        """Минус 1 к значению использований у пользователя"""
        query = "UPDATE tgcalc_user_settings SET uses_count = %s WHERE user_id = %s"
        uses_count = self.get_calculator_uses_count(user_id) or 1
        params = (uses_count - 1, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[minus_calculator_uses_count]: {e}')
            self.connection.rollback()
            return False

        pass

    def get_calculator_tp_show(self, user_id: int):
        """Получить коэфициенты тейк профит на показ"""
        query = 'SELECT take_profit_to_show FROM tgcalc_user_settings WHERE user_id = %s'
        params = (user_id,)
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data.get('take_profit_to_show') if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_calculator_tp_show]: {e}')
            self.connection.rollback()
            return None

    def set_calculator_tp_show(self, user_id: int, tp: str):
        """Установить коэфициенты тейк профит на показ"""
        query = "UPDATE tgcalc_user_settings SET take_profit_to_show = %s WHERE user_id = %s"
        params = (tp, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculator_tp_show]: {e}')
            self.connection.rollback()
            return False

    def get_calculator_user_market(self, user_id: int) -> MARKETS_TYPE | None:
        """Получить рынок пользователя"""
        query = 'SELECT market FROM tgcalc_user_settings WHERE user_id = %s'
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if data is None else data['market']
        except Exception as e:
            print(f'ERROR[get_calculator_user_market]: {e}')
            self.connection.rollback()
            return None

    def set_calculator_user_market(self, user_id: int, market: MARKETS_TYPE):
        """Установить рынок пользователя"""
        query = "UPDATE tgcalc_user_settings SET market = %s WHERE user_id = %s"
        params = (market, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculator_user_market]: {e}')
            self.connection.rollback()
            return False

    def get_user_is_splitting(self, user_id: int) -> bool:
        query = 'SELECT is_splitting FROM tgcalc_user_settings WHERE user_id = %s'
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return False if data is None else data.get('is_splitting') == 1
        except Exception as e:
            print(f'ERROR[get_user_is_splitting]: {e}')
            self.connection.rollback()
            return False

    def set_user_is_splitting(self, user_id: int, value: bool):
        query = 'UPDATE tgcalc_user_settings SET is_splitting = %s WHERE user_id = %s'
        params = (int(value), user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_is_splitting]: {e}')
            self.connection.rollback()
            return False

    def get_user_split_values(self, user_id: int) -> list[float] | None:
        query = 'SELECT split_values FROM tgcalc_user_settings WHERE user_id = %s'
        params = (user_id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if data is None else data.get('split_values')
        except Exception as e:
            print(f'ERROR[get_user_split_values]: {e}')
            self.connection.rollback()
            return None

    def set_user_split_values(self, user_id: int, values: list[float]):
        query = 'UPDATE tgcalc_user_settings SET split_values = %s WHERE user_id = %s'
        params = (values, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_split_values]: {e}')
            self.connection.rollback()
            return False

    def reset_user_settings(self, user_id: int):
        query = (
            'UPDATE tgcalc_user_settings SET take_profit_to_show = %s, market = %s, base_currency = %s, '
            'base_deposit = %s, base_risk_percent = %s '
            'WHERE user_id = %s'
        )
        params = ('345', 'crypto', 'USD', None, None, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[reset_user_settings]: {e}')
            self.connection.rollback()
            return False

    # Workers
    def _data_to_worker(self, data: DictRow):
        return Worker(
            id=data.get('id'),
            tg_id=data.get('id_telegram') or 0,
            username=data.get('username_tg') or '',
            role=data.get('role')
        )

    WORKER_QUERY = (
        'SELECT w.user_id as id, w.role, u.id_telegram, u.username_tg FROM tgbot_workers as w '
        'LEFT JOIN users as u ON u.id = w.user_id '
    )

    def add_worker(self, id: int, role: int):
        """Добваление работника (1 = админ, 2 = редактор)"""
        datetime_now = datetime.utcnow()
        query = "INSERT INTO tgbot_workers(user_id, role, created_at, updated_at) VALUES(%s, %s, %s, %s)"
        params = (id, role, datetime_now, datetime_now)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_worker]: {e}')
            self.connection.rollback()
            return False

    def del_worker(self, id: int):
        """Удаление работника"""
        query = 'DELETE FROM tgbot_workers WHERE user_id = %s'
        params = (id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[del_worker]: {e}')
            self.connection.rollback()
            return False

    def get_all_workes(self) -> list[Worker]:
        """Получить всех работников"""
        query = self.WORKER_QUERY

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_worker(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_all_workes]: {e}')
            self.connection.rollback()
            return []

    def get_admins(self) -> list[Worker]:
        """Получить всех админов"""
        query = self.WORKER_QUERY + 'WHERE w.role = 1'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_worker(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_admins]: {e}')
            self.connection.rollback()
            return []

    def get_redactors(self) -> list[Worker]:
        """Получить всех редакторов"""
        query = self.WORKER_QUERY + 'WHERE w.role = 2'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_worker(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_redactors]: {e}')
            self.connection.rollback()
            return []

    def get_support_name(self) -> str:
        """Получение тех. поддержки"""
        query = self.WORKER_QUERY + 'WHERE w.role = 3'

        try:
            self.curs.execute(query)
            data = self.curs.fetchone()
            return data.get('username_tg', '') if (data is not None) else ''
        except Exception as e:
            print(f'ERROR[get_support_name]: {e}')
            self.connection.rollback()
            return ''

    def update_support(self, id: int):
        """Изменение тех. поддержки"""
        query = 'UPDATE tgbot_workers SET user_id = %s WHERE role = 3'
        params = id,

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_support]: {e}')
            self.connection.rollback()
            return False

    def get_worker_role(self, id: int) -> int | None:
        """Узнать роль работника"""
        query = "SELECT role FROM tgbot_workers WHERE user_id = %s"
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data.get('role') if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_worker_role]: {e}')
            self.connection.rollback()
            return None

    # Auth
    def get_access_token(self):
        query = 'SELECT value FROM access_options WHERE name = %s'
        params = ('tg_api_auth_token',)

        try:
            self.curs.execute(query, params)
            res = self.curs.fetchone()
            return res['value'] if res is not None else None
        except Exception as e:
            print(f'ERROR[get_access_token]: {e}')
            self.connection.rollback()
            return None

    # Options
    def set_option(self, name, value):
        datetime_now = datetime.now()
        query = "UPDATE tgbot_options set value = %s, updated_at = %s WHERE name_option = %s"
        params = (value, datetime_now, name,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_option]: {e}')
            self.connection.rollback()
            return False

    def get_option(self, name):
        query = 'SELECT value FROM tgbot_options WHERE name_option = %s'
        params = (name,)

        try:
            self.curs.execute(query, params)
            res = self.curs.fetchone()
            return res['value'] if res is not None else None
        except Exception as e:
            print(f'ERROR[get_option]: {e}')
            self.connection.rollback()
            return None

    # Posts
    def _data_to_post(self, data: DictRow):
        open_price, stop_loss, name, ticker = (
            data.get('open_price'),
            data.get('stop_loss'),
            data.get('name'),
            data.get('ticker')
        )
        details = None

        if (
            open_price is not None
            and stop_loss is not None
            and name is not None
            and ticker is not None
        ):
            details = PostDetails(
                name=name,
                open_price=open_price,
                stop_loss=stop_loss,
                ticker=ticker
            )

        return Post(
            id=data.get('id'),
            content=data.get('content'),
            mes_type=data.get('message_type'),
            media=data.get('media'),
            direct=data.get('direct') or '',
            date_time=data.get('date_time'),
            details=details
        )

    def add_post(self, post: Post):
        """Добавить отложенный пост"""
        if post.details is None:
            details = (None, None, None, None)
        else:
            details = (
                post.details.open_price,
                post.details.stop_loss,
                post.details.name,
                post.details.ticker
            )

        query = """
            INSERT INTO tgbot_posts (content, message_type, media, direct, date_time, open_price, stop_loss, name, ticker)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (post.content, post.mes_type, post.media,
                  post.direct, post.date_time, *details)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_post]: {e}')
            self.connection.rollback()
            return False

    def delete_post(self, post_id: int):
        """Удалить отложенный пост"""
        try:
            self.curs.execute(
                "DELETE FROM tgbot_posts WHERE id = %s", (post_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[delete_post]: {e}')
            self.connection.rollback()
            return False

    def get_all_posts(self) -> list[Post]:
        """Получение отложенных постов"""
        query = 'SELECT * FROM tgbot_posts'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_post(el), data))
        except Exception as e:
            print(f'ERROR[get_all_posts]: {e}')
            self.connection.rollback()
            return []

    def get_post(self, id: int):
        """Получить отложенный пост по id"""
        query = 'SELECT * FROM tgbot_posts WHERE id = ?'
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_post(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_post]: {e}')
            self.connection.rollback()
            return None

    # Texts
    def _data_to_text(self, data: DictRow):
        return Text(
            id=data.get('id'),
            name=data.get('name'),
            message=data.get('message') or '',
            message_type=data.get('message_type') or 'text',
            media_id=data.get('media_id') or ''
        )

    def get_texts(self) -> list[Text]:
        query = 'SELECT * FROM tgbot_texts'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_text(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_texts]: {e}')
            self.connection.rollback()
            return []

    def get_text_by_name(self, name: str):
        query = 'SELECT * FROM tgbot_texts WHERE name = %s'
        params = (name,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_text(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_text_by_name]: {e}')
            self.connection.rollback()
            return None

    def update_text(self, name: str, text: str):
        mes_type = 'text'
        check_text = self.get_text_by_name(name)

        try:
            if check_text is None:
                query = 'INSERT INTO tgbot_texts(message, message_type, name) VALUES(%s, %s, %s)'
            else:
                query = 'UPDATE tgbot_texts SET message = %s, message_type = %s WHERE name = %s'

            params = (text, mes_type, name)

            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_text]: {e}')
            self.connection.rollback()
            return False

    # Future
    def _data_to_future(self, data: DictRow):
        return Future(
            id=data.get('id'),
            name=data.get('name'),
            step=data.get('step'),
            price_step=data.get('price_step')
        )

    def get_future(self, name: str):
        name = name.upper()
        query = 'SELECT * FROM tgbot_futures WHERE name = %s'
        params = (name,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_future(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_future]: {e}')
            self.connection.rollback()
            return None

    def update_future(self, name: str, step: float, price_step: float):
        check_future = self.get_future(name)

        try:
            if check_future is None:
                query = 'INSERT INTO tgbot_futures(step, price_step, name) VALUES(%s, %s, %s)'
            else:
                query = 'UPDATE tgbot_futures SET step = %s, price_step = %s WHERE name = %s'

            params = (step, price_step, name)

            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_future]: {e}')
            self.connection.rollback()
            return False

    # Forexes
    def _data_to_forex(self, data: DictRow):
        return Forex(
            id=data.get('id'),
            pair=data.get('pair'),
            price=data.get('price'),
            help_pair=data.get('help_pair')
        )

    def get_forex(self, pair: str):
        query = 'SELECT * FROM tgbot_forexes WHERE pair = %s'
        params = (pair,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_forex(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_forex]: {e}')
            self.connection.rollback()
            return None

    def update_forex(self, pair: str, price: float, help_pair: str | None = None):
        check_forex = self.get_forex(pair)
        params = (pair, price, help_pair)

        try:
            if check_forex is None:
                query = 'INSERT INTO tgbot_forexes (pair, price, help_pair) VALUES (%s, %s, %s)'
                params = (pair, price, help_pair)
            else:
                query = 'UPDATE tgbot_forexes SET price = %s, help_pair = %s WHERE pair = %s'
                params = (price, help_pair or check_forex.help_pair, pair)

            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_forex]: {e}')
            self.connection.rollback()
            return False


db_new = Database(DB_PG_USER, DB_PG_PASS, DB_PG_HOST, DB_PG_PORT, DB_PG_NAME)
