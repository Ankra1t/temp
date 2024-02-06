import sqlite3
from typing import Any, Literal, Optional

from models import Post, PostDetails
from db_new import BASE_VALUE_TYPE, LANGUAGES_TYPE, MARKETS_TYPE


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.curs = self.connection.cursor()

    def get_pay_money(self, id: int):  # TODO
        """Получить потраченную сумму юзера"""
        query = "SELECT pay_money FROM users WHERE id = ?"
        params = (id,)

        try:
            return int(self.curs.execute(query, params).fetchone()[0])
        except Exception as e:
            print(f'ERROR[get_pay_money]: {e}')
            return None

    def get_balance(self, id: int):  # TODO
        """Получаем баланс юзера"""
        query = "SELECT balance FROM users WHERE id = ?"
        params = (id,)
        try:
            return int(self.curs.execute(query, params).fetchone()[0])
        except Exception as e:
            print(f'ERROR[get_balance]: {e}')
            return None

    def get_users_with_sub(self):  # TODO
        """Получить список пользователей с активной подпиской"""
        try:
            return self.curs.execute(
                "SELECT * FROM users WHERE count_days > 0").fetchall()
        except Exception as e:
            print(f'ERROR[get_users_with_sub]: {e}')
            return []

    def get_users_without_sub(self):  # TODO
        """Получить список бесплатников"""
        try:
            return self.curs.execute(
                "SELECT * FROM users WHERE count_days = 0").fetchall()
        except Exception as e:
            print(f'ERROR[get_users_without_sub]: {e}')
            return []

    def get_users_with_more_pay(self):  # TODO
        """Получить список пользователей с более 1 покупкой"""
        try:
            return self.curs.execute(
                "SELECT * FROM users WHERE count_sub > 1").fetchall()
        except Exception as e:
            print(f'ERROR[get_users_with_more_pay]: {e}')
            return []

# ======================= // ANCHOR FOREX
    def add_forex(self, paire: str, price: float, help_paire: str | None = None):
        query = 'INSERT INTO forexes (paire, price, help_paire) VALUES (?,?,?)'
        params = (paire, price, help_paire)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except:
            return False

    def update_price_forex(self, price, paire):
        self.curs.execute(
            f"UPDATE forexes set price = ? WHERE paire = ?", (price, paire))
        self.connection.commit()

    def get_all_forex_btn(self):
        # WHERE paire != 'USD/RUB'
        result = self.curs.execute(
            "SELECT DISTINCT paire FROM forexes ORDER BY paire COLLATE NOCASE ASC").fetchall()
        return result

    def get_forex_rub_price(self):
        result = self.curs.execute(
            "SELECT price FROM forexes WHERE paire = 'USD/RUB'").fetchone()
        return result

    def get_price_forex(self, paire: str) -> float | None:
        try:
            return self.curs.execute(
                "SELECT price FROM forexes WHERE paire = ?", (paire,)).fetchone()[0]
        except:
            return None

    def get_help_paire_forex(self, paire: str) -> str | None:
        try:
            return self.curs.execute(
                "SELECT help_paire FROM forexes WHERE paire = ?", (paire,)).fetchone()[0]
        except:
            return None


# ======================= // Управление Баном Пользователей
    def get_subsribe_users(self, today, date_bonus):
        res = self.curs.execute(f"SELECT u.id_idx, u.created_at, u.username, "
                                f"u.count_sub, "
                                f"u.count_days, "
                                f"u.refer, "
                                f"u.pay_money, "
                                f"u.balance, "
                                f"u.count_les, "
                                f"u.id, "
                                f"u.ban "
                                f"FROM subscribes AS sub, users AS u "
                                f"WHERE "
                                f"(sub.finish_dt > ? OR sub.finish_dt > ?) "
                                f"AND sub.active = 1 "
                                f"AND u.ban IS NULL "
                                f"AND u.id = sub.tg_user_id",
                                (today, date_bonus,)).fetchall()
        return res

    def get_subsribe_more1_users(self):
        # todo-fin: Как получить пользователей с кол-во подписок больше 1
        res = self.curs.execute(f"SELECT u.id_idx, u.created_at, u.username, "
                                f"u.count_sub, "
                                f"u.count_days, "
                                f"u.refer, "
                                f"u.pay_money, "
                                f"u.balance, "
                                f"u.count_les, "
                                f"u.id, "
                                f"u.ban "
                                f"FROM subscribes AS sub, users AS u "
                                f"WHERE "
                                f"(SELECT COUNT(*) FROM subscribes AS s "
                                f"WHERE s.tg_user_id == sub.tg_user_id AND s.subscribe_type = ?) > 1 "
                                f"AND u.ban IS NULL "
                                f"AND u.id = sub.tg_user_id",
                                ('paid',)).fetchall()
        return res


db = Database('4p_bot.db')
