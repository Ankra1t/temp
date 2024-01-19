from datetime import datetime
from typing import Literal
import psycopg2
from psycopg2.extras import DictCursor, DictRow

from common.vars import DATE_FORMAT
from config_global import DB_PG_HOST, DB_PG_NAME, DB_PG_PASS, DB_PG_PORT, DB_PG_USER
from models import Price, Subscribe, Transactions

SUBSCRIBE_TYPE = Literal['trial', 'paid']


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

    # Prices
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
        )

    def get_prices(self, active: int) -> list[Price]:
        """Получение тарифа"""
        query = """SELECT * FROM prices WHERE active = %s"""
        params = (active,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_price(el), data))
        except Exception as e:
            print(f'ERROR[get_prices]: {e}')
            self.connection.rollback()
            return []

    def get_price_by_id(self, id: int):
        query = "SELECT * FROM prices WHERE id = %s"
        params = (id,)
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

    def get_price_by_name(self, name: str):
        """Получение цены по имени"""
        query = "SELECT * FROM prices WHERE name = %s "
        params = (name,)

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
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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
        datetime_now = datetime.now()
        query = ("INSERT INTO prices "
                 "(name, currency, price, description, img, duration_days, updated_at, created_at) "
                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)")
        params = (data.name, data.currency, data.price, data.description,
                  data.img, data.duration_days, datetime_now, datetime_now)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f'ERROR[add_price]: {e}')
            self.connection.rollback()

    def deactive_price(self, id: int):
        """Установить цену не активной"""
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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
        datetime_now = datetime.now()
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

    # Subscribe
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

    def get_users_finished_subscribe(self, type: SUBSCRIBE_TYPE) -> list[DictRow]:
        datetime_now = datetime.now().strftime(DATE_FORMAT)
        query = (
            'SELECT u.id_idx, u.created_at, u.username, u.count_sub, u.count_days, '
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
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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

    def set_subscribe_findate(self, subscribe_id: int, finish_date: str):
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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

    def set_unactive_subscribes(self, type: SUBSCRIBE_TYPE):
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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
            print(f'ERROR[set_unactive_trial_subscribes]: {e}')
            self.connection.rollback()
            return False

    def set_unactive_subscribe_for_time(self, time_start: str, time_end: str):
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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

    # Transactions
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

    def set_transactions_complete(self, id: int):
        datetime_now = datetime.now().strftime(DATE_FORMAT)
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


db_new = Database(DB_PG_USER, DB_PG_PASS, DB_PG_HOST, DB_PG_PORT, DB_PG_NAME)
