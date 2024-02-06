import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.curs = self.connection.cursor()

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
