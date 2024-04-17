from datetime import datetime
import json
from locale import currency
from typing import Literal, Optional
import psycopg2
from psycopg2.extras import DictCursor, DictRow

from common.dt import get_datetime_now
from config_global import DB_PG_HOST, DB_PG_NAME, DB_PG_PASS, DB_PG_PORT, DB_PG_USER

from models import (
    Calculation, Forex, ForexInfo, Future, Post, PostDetails,
    Text, UserCalcSettings, UserInfo, Price, Subscribe,
    Transactions, Purchase, Worker, Task,
    MARKETS_TYPE
)

SUBSCRIBE_TYPE = Literal['trial', 'paid']
BASE_VALUE_TYPE = Literal['base_deposit', 'base_risk', 'base_currency']
SORT_BY_TYPE = Literal['new', 'old']

LANGUAGES_TYPE = Literal['ru', 'en']
LANGUAGES: tuple[LANGUAGES_TYPE, ...] = ('ru', 'en')


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
            id=data.get('id'),
            name=data.get('name'),
            duration=data.get('duration_days'),
            price=data.get('price'),
            currency=data.get('currency'),
            image=data.get('img'),
            img_en=data.get('img_en'),
            description=data.get('description'),
            discount_percent=data.get('discount_percent'),
            discount_findate=data.get('discount_findate'),
            type_product=data.get('type_product'),
            switch_active=data.get('switch_active'),
            price_findate=data.get('price_findate'),
        )

    def get_prices(self, active: int = 1, switch_active: int | None = None) -> list[Price]:
        """Получение тарифа"""
        self.check_tariffs_datetime()

        if switch_active is None:
            query = 'SELECT * FROM prices WHERE active = %s'
            params = (active,)
        else:
            query = 'SELECT * FROM prices WHERE active = %s AND switch_active = %s'
            params = (active, switch_active)

        query += ' ORDER BY id ASC'

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_price(el), data))
        except Exception as e:
            print(f'ERROR[get_prices]: {e}')
            self.connection.rollback()
            return []

    def get_prices_by_product(self, product_type: str, active: int, switch_active: int | None = None) -> list[Price]:
        """Получение тарифа по типу продукта"""
        self.check_tariffs_datetime()

        if switch_active is None:
            query = """SELECT * FROM prices WHERE active = %s AND type_product = %s"""
            params = (active, product_type)
        else:
            query = """SELECT * FROM prices WHERE active = %s AND type_product = %s AND switch_active = %s"""
            params = (active, product_type, switch_active)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_price(el), data))
        except Exception as e:
            print(f'ERROR[get_prices_by_product]: {e}')
            self.connection.rollback()
            return []

    def get_price_by_id(self, id: int, switch_active: int | None = None):
        if switch_active is None:
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

    def update_price_name(self, id: int, value: str):
        query = "UPDATE prices SET name = %s WHERE id = %s"
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price_name]: {e}')
            self.connection.rollback()
            return False

    def update_price_price(self, id: int, value: float):
        """Обновить цену"""
        query = "UPDATE prices SET price = %s WHERE id = %s"
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price_price]: {e}')
            self.connection.rollback()
            return False

    def update_price_duration(self, id: int, value: int):
        """Обновить цену"""
        query = "UPDATE prices SET duration_days = %s WHERE id = %s"
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price_duration]: {e}')
            self.connection.rollback()
            return False

    def update_price_image(self, id: int, value: str):
        """Обновить цену"""
        query = "UPDATE prices SET img = %s WHERE id = %s"
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price_image]: {e}')
            self.connection.rollback()
            return False

    def update_price_image_en(self, id: int, value: str):
        """Обновить цену"""
        query = "UPDATE prices SET img_en = %s WHERE id = %s"
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price_image_en]: {e}')
            self.connection.rollback()
            return False

    def update_price_description(self, id: int, value: str):
        """Обновить цену"""
        query = "UPDATE prices SET description = %s WHERE id = %s"
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_price_description]: {e}')
            self.connection.rollback()
            return False

    def add_price(self, data: Price):
        """Добавление цены"""
        query = ("INSERT INTO prices "
                 "(name, currency, price, description, img, duration_days, type_product) "
                 "VALUES(%s, %s, %s, %s, %s, %s, %s)")
        params = (data.name, data.currency, data.price, data.description,
                  data.img, data.duration_days, data.type_product)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f'ERROR[add_price]: {e}')
            self.connection.rollback()

    def deactive_price(self, id: int):
        """Установить цену не активной"""
        query = "UPDATE prices set active = 0 WHERE id = %s"
        params = (id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[deactive_price]: {e}')
            self.connection.rollback()
            return False

    def set_price_discount(self, id: int, percent: float, fin_date: datetime):
        """Установка скидки тарифа"""
        query = "UPDATE prices set discount_percent = %s, discount_findate = %s WHERE id = %s"
        params = (percent, fin_date, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_price_discount]: {e}')
            self.connection.rollback()
            return False

    def delete_price_discount(self, id: int):
        """Удаление скидки тарифа"""
        query = "UPDATE prices set discount_percent = %s, discount_findate = %s WHERE id = %s"
        params = (None, None, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[delete_price_discount]: {e}')
            self.connection.rollback()
            return False

    def get_first_tariff_by_product(self, product='signals', active=1, switch_active=1):
        """Получить первый активный включенный тариф по продукту"""
        query = "SELECT * FROM prices WHERE type_product = %s AND active = %s AND switch_active = %s"
        params = (product, active, switch_active,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            if data is None:
                return None

            return self._data_to_price(data)
        except Exception as e:
            print(f'ERROR[get_first_price_by_product]: {e}')
            self.connection.rollback()
            return None

    def switch_tariff(self, tariff_id: int, switch_active: int):
        """Включить или выключить тариф"""
        query = "UPDATE prices set switch_active = %s WHERE id = %s"
        params = (switch_active, tariff_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[switch_tariff]: {e}')
            self.connection.rollback()
            return False

    def set_findate_tariff(self, tariff_id: int, fin_date: datetime | None):
        """Установить дату окончания тарифа"""
        query = "UPDATE prices set price_findate = %s WHERE id = %s"
        params = (fin_date, tariff_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_findate_tariff]: {e}')
            self.connection.rollback()
            return False

    def check_tariffs_datetime(self):
        """Установить дату окончания тарифа"""
        now = get_datetime_now()
        query_finish = "UPDATE prices set switch_active = %s, price_findate = %s WHERE price_findate < %s"
        params_finish = (0, None, now)

        query_discount = 'UPDATE prices set discount_percent = %s, discount_findate = %s WHERE discount_findate < %s'
        params_discount = (None, None, now)

        try:
            self.curs.execute(query_finish, params_finish)
            self.curs.execute(query_discount, params_discount)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[check_tariffs_datetime]: {e}')
            self.connection.rollback()
            return False

    # # # # # # # # Subscribes # # # # # # # #
    def _data_to_subsbscribe(self, data: DictRow):
        return Subscribe(
            id=data.get('id'),
            user_id=data.get('user_id'),
            finish_dt=data.get('finish_dt'),
            product_type=data.get('subscribe_type'),
            active=data.get('active'),
            transactions_payed_id=data.get('transactions_payed_id'),
        )

    def add_subsbscribe(self, sub: Subscribe):
        query = ("INSERT INTO "
                 "subscribes (user_id, finish_dt, subscribe_type, active, transactions_payed_id) "
                 "VALUES (%s, %s, %s, %s, %s)")
        params = (
            sub.user_id, sub.finish_dt, sub.product_type, sub.active, sub.transactions_payed_id
        )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_subsbscribe]: {e}')
            self.connection.rollback()
            return False

    def get_current_subscribe_user(self, user_id: int):
        query = 'SELECT * FROM subscribes WHERE user_id = %s AND active = %s'
        params = (user_id, True)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if data is None else self._data_to_subsbscribe(data)
        except Exception as e:
            print(f'ERROR[get_current_subscribe_user]: {e}')
            self.connection.rollback()
            return None

    def get_user_trial_subscribe(self, user_id: int):
        query = "SELECT * FROM subscribes WHERE user_id = %s AND subscribe_type = %s"
        params = (user_id, 'trial')

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()

            return data if (data is None) else self._data_to_subsbscribe(data)
        except Exception as e:
            print(f'ERROR[get_user_trial_subscribe]: {e}')
            self.connection.rollback()
            return None

    def get_users_finished_subscribe(self, type: SUBSCRIBE_TYPE) -> list[UserInfo]:
        datetime_now = get_datetime_now()
        query = (
            'SELECT u.* FROM users as u JOIN subscribes as sub ON sub.user_id = u.id '
            'WHERE sub.finish_dt < %s AND sub.active = %s '
            f'AND sub.transactions_payed_id is {"not" if type == "paid" else ""} NULL'
        )
        params = (datetime_now, True)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data))
        except Exception as e:
            print(f'ERROR[get_users_finished_subscribe]: {e}')
            self.connection.rollback()
            return []

    def set_subscribe_unactive_by_user_id(self, user_id: int):
        query = "UPDATE subscribes set active = %s WHERE user_id = %s"
        params = (False, user_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_subscribe_unactive_by_user_id]: {e}')
            self.connection.rollback()
            return False

    def set_subscribe_unactive(self, subscribe_id: int):
        query = "UPDATE subscribes set active = %s WHERE id = %s"
        params = (False, subscribe_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_subscribe_unactive]: {e}')
            self.connection.rollback()
            return False

    def set_trial_subscribe_unactive_by_user(self, user_id: int):
        query = "UPDATE subscribes set active = %s WHERE user_id = %s AND subscribe_type = %s"
        params = (False, user_id, 'trial')

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_trial_subscribe_unactive_by_user]: {e}')
            self.connection.rollback()
            return False

    def set_subscribe_findate(self, subscribe_id: int, finish_date: datetime):
        query = "UPDATE subscribes set finish_dt = %s WHERE id = %s"
        params = (finish_date, subscribe_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_subscribe_findate]: {e}')
            self.connection.rollback()
            return False

    def deactivate_subscribe(self, subscribe_id: int):
        query = (
            'UPDATE subscribes set active = %s '
            'WHERE id = %s'
        )
        params = (False, subscribe_id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_deactivate_subscribe]: {e}')
            self.connection.rollback()
            return False

    def check_unactive_subscribes(self, type: SUBSCRIBE_TYPE):
        datetime_now = get_datetime_now()
        query = (
            'UPDATE subscribes set active = %s '
            'WHERE finish_dt < %s AND subscribe_type = %s'
        )
        params = (False, datetime_now, type, )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_unactive_subscribes]: {e}')
            self.connection.rollback()
            return False

    def set_unactive_subscribe_for_time(self, time_start: datetime, time_end: datetime):
        query = (
            "UPDATE subscribes set active = %s "
            "WHERE (updated_at BETWEEN %s AND %s ) AND active = %s"
        )
        params = (False, time_start, time_end, True,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_unactive_trial_subscribes]: {e}')
            return False

    def get_active_subscribes_by_user_id(self, user_id: int):
        query = 'SELECT * FROM subscribes WHERE user_id = %s AND active = %s'
        params = (user_id, True)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_subsbscribe(el), data))

        except Exception as e:
            print(f'ERROR[get_active_subscribes_by_user_id]: {e}')
            self.connection.rollback()
            return None

    def get_active_subscribes_all_users(self, ban: bool):
        """Получить активные подписки для всех пользователей"""
        query = (
            'SELECT u.id AS id, u.id_telegram AS id_telegram, u.username_tg AS username_tg,  '
            'ub.refer_id AS refer_id, u.ban AS ban, u.created_at AS created_at '
            'FROM subscribes sub, users u, prices p, tgbotusers ub '
            'WHERE '
            '(sub.subscribe_type = %s OR sub.subscribe_type = %s) '
            'AND sub.active = %s AND sub.user_id = u.id '
            'AND sub.prices_id = p.id '
            'AND ub.user_id = u.id '
            'AND (p.type_product = %s OR p.type_product = %s) '
            'AND u.ban = %s '
        )
        print(query)
        params = ('paid', 'trial', 1, 'signals', 'calc_signals', ban, )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data))
        except Exception as e:
            print(f'ERROR[get_active_subscribes_all_users]: {e}')
            self.connection.rollback()
            return []

        pass

    # def _data_to_client(self, data: DictRow):
    #     return Client(
    #         user=UserInfo(
    #             data.get('user_id')
    #         ),
    #         subscribes=Subscribe(

    #         )
    #     )

    # # # # # # # #  Transactions
    def _data_to_transaction(self, data: DictRow):
        return Transactions(
            id=data.get('id'),
            user_id=data.get('user_id'),
            code=data.get('code'),
            link=data.get('link'),
            sum=data.get('sum'),
            currency=data.get('currency'),
            status=data.get('status'),
            payment_date=data.get('payment_date'),
            name=data.get('name'),
            duration_days=data.get('duration_days'),
            type_product=data.get('type_product'),
        )

    def add_transaction(
        self,
        user_id: int,
        code: str,
        link: Optional[str],
        sum: float,
        status: str,
        currency: str,
        name: str,
        duration_days: int,
        type_product: str
    ):
        query = (
            "INSERT INTO transactions"
            "(user_id, code, link, sum, currency, status, name, duration_days, type_product) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (user_id, code, link, sum, currency,
                  status, name, duration_days, type_product)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_transaction]: {e}')
            self.connection.rollback()
            return False

    def get_wait_transaction(self, code: str):
        query = (
            "SELECT * FROM transactions "
            "WHERE code = %s AND status = %s"
        )
        params = (code, 'wait_payments')

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if data is None else self._data_to_transaction(data)
        except Exception as e:
            print(f'ERROR[get_wait_transaction]: {e}')
            self.connection.rollback()
            return None

    def get_paid_transactions_by_user(self, user_id: int) -> list[Transactions]:
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

    def get_paid_transactions_all(self) -> list[Transactions]:
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

    def get_paid_users_count(self) -> int:  # TODO
        """Получить все оплаченные транзакции"""
        query = "SELECT user_id FROM transactions WHERE status = %s GROUP BY user_id"
        params = ('paid',)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return len(data)
        except Exception as e:
            print(f'ERROR[get_paid_users_count]: {e}')
            self.connection.rollback()
            return 0

    # TODO
    def get_paid_transactions_period(self, start_date, fin_date) -> list[Transactions]:
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

    def get_paid_transactions_product(self, product) -> list[Transactions]:
        """Получить все оплаченные транзакции по продукту"""
        query = ("SELECT * "
                 "FROM transactions "
                 "WHERE type_product = %s AND status = %s "
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

    def get_paid_transactions_summ(self) -> int:
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
            return 0

    def get_paid_transactions_summ_period(self, start_date, fin_date) -> int:
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
            return 0

    def get_paid_transactions_summ_product(self, product) -> int:
        """Суммы по транзакциям по продукту"""
        query = ("SELECT sum(sum) "
                 "FROM transactions "
                 "WHERE type_product = %s "
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
            return 0

    def get_purchases_by_user(self, user_id: int) -> list[Purchase]:
        """Получение покупок пользователя"""
        query = ("SELECT * "
                 "FROM transactions "
                 "WHERE "
                 "user_id = %s AND status = %s "
                 )
        status = 'paid'
        params = (user_id, status,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()

            return list(map(lambda el: self._data_to_purchase(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_by_user]: {e}')
            self.connection.rollback()
            return []

    # TODO - only transactions
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

    def get_purchases_all_users(self) -> list[Purchase]:
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

            return list(map(lambda el: self._data_to_purchase(el), data))
        except Exception as e:
            print(f'ERROR[get_paid_transactions_by_user]: {e}')
            self.connection.rollback()
            return []

    def success_transaction(self, id: int):
        datetime_now = get_datetime_now()
        query = "UPDATE transactions set status = %s, payment_date = %s, created_at = %s WHERE id = %s"
        params = ('paid', datetime_now, datetime_now, id, )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[success_transaction]: {e}')
            self.connection.rollback()
            return False

    def cancel_transaction(self, id: int):
        query = "DELETE FROM transactions WHERE id = %s"
        params = (id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[cancel_transaction]: {e}')
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
            registration_dt=data.get('created_at') or datetime(2012, 12, 12)
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

    def create_tg_user_settings(self, id: int, market: MARKETS_TYPE):
        query = 'INSERT INTO tgcalc_user_settings (user_id, market, base_currency) VALUES (%s, %s, %s)'

        currency = None
        if market == 'crypto':
            currency = 'USDT'

        params = id, market, currency

        self.curs.execute(query, params)
        self.connection.commit()

    def create_tg_user_tables(self, id: int):
        query = 'INSERT INTO tgbotusers (user_id) VALUES (%s)'
        params = id,

        try:
            self.curs.execute(query, params)
            self.create_tg_user_settings(id, 'crypto')
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR [create_tg_user_tables]: {e}')
            self.connection.rollback()
            return False

    def get_paginated_users(self, limit=6, page=1, sort_by: SORT_BY_TYPE = 'new') -> list[UserInfo]:
        """Получить постраничный список пользователей"""
        query = self.USER_INFO_QUERY
        query += f"ORDER BY u.created_at {'ASC' if sort_by == 'old' else 'DESC'}, u.id ASC "
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

    def get_banned_users(self, limit: int | None = None, page=1, sort_by: SORT_BY_TYPE = 'new') -> list[UserInfo]:
        """
            Получение забаненных пользователей\n
            Если не задан лимит, то вернуться все забаненные пользователи
        """
        params = None

        query = self.USER_INFO_QUERY + 'WHERE u.ban = 1 '
        query += f"ORDER BY u.created_at {'ASC' if sort_by == 'old' else 'DESC'}, u.id ASC "

        if limit is not None:
            query += "LIMIT %s OFFSET %s "
            params = (limit, (page - 1) * limit)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda u: self._data_to_user(u), data))
        except Exception as e:
            print(f'ERROR[get_banned_users]: {e}')
            self.connection.rollback()
            return []

    def get_subsribed_users(self, min_sub_count=1) -> list[UserInfo]:
        query = self.USER_INFO_QUERY + (
            'WHERE u.ban = 0 '
            f'AND '
            f'(SELECT COUNT (*) FROM subscribes as sub '
            f'WHERE sub.user_id = u.id '
            f'AND sub.transactions_payed_id IS NOT NULL) >= %s '
            'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.user_id = u.id AND sub.active = %s) > 0 '
        )
        params = (min_sub_count, True)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_user(el), data)) if (data is not None) else []
        except Exception as e:
            print(f'ERROR[get_subsribed_users]: {e}')
            self.connection.rollback()
            return []

    def get_not_subscribed_users(self) -> list[UserInfo]:
        query = self.USER_INFO_QUERY + (
            'WHERE u.ban = 0 '
            'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.user_id = u.id AND sub.active = %s) = 0 '
        )
        params = True,

        try:
            self.curs.execute(query, params)
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

    # # # # # # # #  Users Сервисные запросы
    def set_task(self, task: Task):
        """Запланировать задание"""
        datetime_now = get_datetime_now()
        query = ("INSERT INTO tgbot_service_tasks("
                 "type_task, user_id, date_action, type_message, text, media_id, "
                 "active, created_at, updated_at) "
                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        params = (task.type_task, task.user_id, task.date_action,
                  task.message.type_message, task.message.text, task.message.media_id,  # type: ignore
                  task.active, datetime_now, datetime_now, )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_task]: {e}')
            self.connection.rollback()
            return False
        pass

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
    def _data_to_user_calc(self, data: DictRow):
        risk_value = data.get('base_risk')
        risk = None if (risk_value is None) else (
            risk_value, data.get('risk_is_percent'))

        day_risk = None
        if data.get('day_risk') is not None:
            value = str(data.get('day_risk', ''))

            is_percent = value.endswith('%')
            value = value.replace('%', '')

            day_risk = float(value), is_percent

        return UserCalcSettings(
            user_id=data.get('user_id'),
            deposit=data.get('base_deposit'),
            risk=risk,
            currency=data.get('base_currency'),
            market=data.get('market') or 'crypto',
            tp_ratio=data.get('take_profit_ratio'),
            split_values=data.get('split_values'),
            trading_style=data.get('trading_style'),
            round_count=data.get('round_count'),
            day_risk=day_risk,
            is_updating_deposit=data.get('is_updating_deposit'),
        )

    def get_user_current_market(self, user_id: int) -> MARKETS_TYPE:
        query = 'SELECT market FROM tgbotusers WHERE user_id = %s'
        params = (user_id,)

        default = 'crypto'
        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            if data is None:
                return default

            return data.get('market')
        except Exception as e:
            print(f'ERROR[get_user_current_market]: {e}')
            self.connection.rollback()
            return default

    def get_calc_user_settings(self, user_id: int) ->  UserCalcSettings | None:
        market = self.get_user_current_market(user_id)

        query = 'SELECT * FROM tgcalc_user_settings WHERE user_id = %s AND market = %s'
        params = user_id, market

        try:
            self.curs.execute(query, params)

            data = self.curs.fetchone()
            if data is None:
                self.create_tg_user_settings(user_id, market)
                return self.get_calc_user_settings(user_id)

            return self._data_to_user_calc(data)
        except Exception as e:
            print(f'ERROR[get_calc_user_settings]: {e}')
            self.connection.rollback()
            return None

    def set_user_base(self, user_id: int, type: BASE_VALUE_TYPE, value: float):
        """Установить значения для автозаполения пользователя"""
        market = self.get_user_current_market(user_id)
        value = round(value, 2)

        query = f'UPDATE tgcalc_user_settings SET {type} = %s WHERE user_id = %s AND market = %s'
        params = (value, user_id, market)

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
        market = self.get_user_current_market(user_id)

        query = 'UPDATE tgcalc_user_settings SET base_currency = %s WHERE user_id = %s AND market = %s'
        params = (value, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_currency]: {e}')
            self.connection.rollback()
            return False

    def set_user_risk_is_percent(self, user_id: int, value: bool):
        market = self.get_user_current_market(user_id)

        query = 'UPDATE tgcalc_user_settings SET risk_is_percent = %s WHERE user_id = %s AND market = %s'
        params = (value, user_id, market)

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

    def get_calculator_uses_count(self, user_id: int) -> int | None:
        """Получить количество использований калькулятора пользователем"""
        query = 'SELECT uses_count FROM tgbotusers WHERE user_id = %s'
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
        query = "UPDATE tgbotusers SET uses_count = %s WHERE user_id = %s"
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

    def get_user_calc_freeze(self, user_id: int) -> datetime | None:
        market = self.get_user_current_market(user_id)

        query = 'SELECT freeze_dt FROM tgcalc_user_settings WHERE user_id = %s AND market = %s'
        params = (user_id, market)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return None if (data is None) else data.get('freeze_dt')
        except Exception as e:
            print(f'ERROR[get_user_calc_freeze]: {e}')
            self.connection.rollback()
            return None

    def set_user_calc_freeze(self, user_id: int, value: datetime | None):
        market = self.get_user_current_market(user_id)

        query = "UPDATE tgcalc_user_settings SET freeze_dt = %s WHERE user_id = %s AND market = %s"
        params = (value, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_calc_freeze]: {e}')
            self.connection.rollback()
            return False

    def set_calculator_tp_ratio(self, user_id: int, tp: list[int]):
        """Установить коэфициенты тейк-профит на показ"""
        market = self.get_user_current_market(user_id)

        query = "UPDATE tgcalc_user_settings SET take_profit_ratio = %s WHERE user_id = %s AND market = %s"
        params = (tp, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculator_tp_ratio]: {e}')
            self.connection.rollback()
            return False

    def set_calculator_user_market(self, user_id: int, market: MARKETS_TYPE):
        """Установить рынок пользователя"""
        query = "UPDATE tgbotusers SET market = %s WHERE user_id = %s"
        params = (market, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculator_user_market]: {e}')
            self.connection.rollback()
            return False

    def set_user_split_values(self, user_id: int, values: list[float] | None):
        market = self.get_user_current_market(user_id)

        query = 'UPDATE tgcalc_user_settings SET split_values = %s WHERE user_id = %s AND market = %s'
        params = (values, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_split_values]: {e}')
            self.connection.rollback()
            return False

    def set_user_day_risk(self, user_id: int, value: float, is_percent=False):
        market = self.get_user_current_market(user_id)
        result = f'{value}{"%" if is_percent else ""}'

        query = 'UPDATE tgcalc_user_settings SET day_risk = %s WHERE user_id = %s AND market = %s'
        params = (result, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_day_risk]: {e}')
            self.connection.rollback()
            return False

    def set_user_round_count(self, user_id: int, value: int):
        market = self.get_user_current_market(user_id)

        query = 'UPDATE tgcalc_user_settings SET round_count = %s WHERE user_id = %s AND market = %s'
        params = (value, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_round_count]: {e}')
            self.connection.rollback()
            return False

    def set_user_trading_style(self, user_id: int, value: str | None):
        market = self.get_user_current_market(user_id)

        query = 'UPDATE tgcalc_user_settings SET trading_style = %s WHERE user_id = %s AND market = %s'
        params = (value, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_trading_style]: {e}')
            self.connection.rollback()
            return False

    def reset_user_settings(self, user_id: int):
        market = self.get_user_current_market(user_id)

        currency = None
        if market == 'crypto':
            currency = 'USDT'

        query = (
            'UPDATE tgcalc_user_settings SET trading_style = %s, '
            'day_risk = %s, round_count = %s, is_updating_deposit = %s, '
            'base_currency = %s, base_deposit = %s, base_risk = %s, '
            'take_profit_ratio = %s, split_values = %s '
            'WHERE user_id = %s AND market = %s'
        )
        params = (None, None, None, False, currency, None, None,
                  [3, 4, 5], None, user_id, market)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[reset_user_settings]: {e}')
            self.connection.rollback()
            return False

    def set_user_updating_deposit(self, user_id: int, value: bool):
        market = self.get_user_current_market(user_id)

        query = 'UPDATE tgcalc_user_settings SET is_updating_deposit = %s WHERE user_id = %s AND market = %s'
        params = value, user_id, market

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_updating_deposit]: {e}')
            self.connection.rollback()
            return False

    # Calc Stats
    def _data_to_calculations(self, data: DictRow):
        pair = data.get('pair')
        pair_price = data.get('pair_price')
        cross_prices = data.get('cross_prices')

        forex = None
        if (pair is not None) and (pair_price is not None) and (cross_prices is not None):
            pairs = str(pair).split('/')
            forex = ForexInfo(
                pair=(pairs[0], pairs[1]),
                price=pair_price,
                cross_prices=json.loads(cross_prices)
            )

        return Calculation(
            id=data.get('id'),
            user_id=data.get('user_id'),
            profit=data.get('profit'),
            in_stat=data.get('in_stat'),
            stat_dt=data.get('stat_dt'),
            deposit=data.get('deposit'),
            risk_value=data.get('risk_value'),
            open_price=data.get('open_price'),
            stop_loss=data.get('stop_loss'),
            round_count=data.get('round_count'),
            currency=data.get('currency'),
            trading_style=data.get('trading_style'),
            market=data.get('market'),
            tp_ratio=data.get('tp_ratio'),
            split_values=data.get('split_values'),
            forex_info=forex,
            tool=data.get('tool'),
        )

    def add_calculation(self, value: Calculation):
        query = (
            'INSERT INTO calculations (user_id, deposit, risk_value, open_price, stop_loss, round_count, '
            'currency, trading_style, market, tp_ratio, split_values, pair, pair_price, cross_prices, tool) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id'
        )

        pair_price = pair = cross_prices = None
        if value.forex_info is not None:
            pair_price = value.forex_info.price
            pair = '/'.join(value.forex_info.pair)
            cross_prices = json.dumps(value.forex_info.cross_prices)

        params = (
            value.user_id, value.deposit, value.risk_value, value.open_price, value.stop_loss,
            value.round_count, value.currency, value.trading_style, value.market,
            value.tp_ratio, value.split_values, pair, pair_price, cross_prices, value.tool
        )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            if data is None:
                raise Exception('Ошибка с записью в БД')

            self.connection.commit()
            return int(data.get('id'))
        except Exception as e:
            print(f'ERROR[add_calculations]: {e}')
            self.connection.rollback()
            return False

    def set_calculation_profit(self, id: int, value: float):
        query = 'UPDATE calculations SET profit = %s WHERE id = %s'
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculations_profit]: {e}')
            self.connection.rollback()
            return False

    def set_calculation_in_stat(self, id: int, value: bool):
        query = 'UPDATE calculations SET in_stat = %s, stat_dt = %s WHERE id = %s'
        params = (value, get_datetime_now(), id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculation_in_stat]: {e}')
            self.connection.rollback()
            return False

    def get_all_calculation(self) -> list[Calculation]:
        query = 'SELECT * FROM calculations'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_calculations(el), data))
        except Exception as e:
            print(f'ERROR[get_all_calculation]: {e}')
            self.connection.rollback()
            return []

    def get_calculations_by_user(self, user_id: int, saved=False) -> list[Calculation]:
        query = 'SELECT * FROM calculations WHERE user_id = %s'
        params = user_id,
        if saved:
            query += ' AND in_stat = %s'
            params = user_id, True

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_calculations(el), data))
        except Exception as e:
            print(f'ERROR[get_calculations_by_user]: {e}')
            self.connection.rollback()
            return []

    def get_calculation(self, id: int):
        query = 'SELECT * FROM calculations WHERE id = %s'
        params = id,

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_calculations(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_calculation]: {e}')
            self.connection.rollback()
            return None

    def get_last_tools(self, user_id: int) -> list[str]:
        query = 'SELECT tool FROM calculations WHERE user_id = %s AND tool is not NULL GROUP BY tool'
        params = user_id,

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: str(el.get('tool') or ''), data))
        except Exception as e:
            print(f'ERROR[get_last_tools]: {e}')
            self.connection.rollback()
            return []

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
        datetime_now = get_datetime_now()
        query = "INSERT INTO tgbot_workers(user_id, role, created_at, updated_at, tg_user_id) VALUES(%s, %s, %s, %s, %s)"
        params = (id, role, datetime_now, datetime_now, 0)

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
        return 'calcsup'
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
        datetime_now = get_datetime_now()
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
            media_id=data.get('media_id') or '',
            media_id_en=data.get('media_id_en')
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


db = Database(DB_PG_USER, DB_PG_PASS, DB_PG_HOST, DB_PG_PORT, DB_PG_NAME)
