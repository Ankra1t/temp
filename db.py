from datetime import datetime
from math import exp
import re
import sqlite3
from tracemalloc import stop
from typing import Any, Literal, Optional

from models import Post, PostDetails

MARKETS_TYPE = Literal['crypto', 'future', 'paper', 'forex']
LANGUAGES_TYPE = Literal['ru', 'en']
LANGUAGES: tuple[LANGUAGES_TYPE, ...] = ('ru', 'en')

BASE_VALUE_TYPE = Literal['base_deposit', 'base_risk_percent', 'base_currency']


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.curs = self.connection.cursor()

    def check_user(self, user_id: int):
        """Проверка: есть ли юзер в системе"""
        query = "SELECT * FROM users WHERE id = ?"
        params = (user_id,)

        try:
            result = self.curs.execute(query, params).fetchall()
        except Exception as e:
            print(f'ERROR[check_user]: {e}')
            result = []

        return bool(len(result))

    def get_user_by_username(self, username: str):
        """Получение пользователя по имени"""
        query = "SELECT * FROM users WHERE username = ?"
        params = (username,)

        try:
            return self.curs.execute(query, params).fetchone()
        except Exception as e:
            print(f'ERROR[get_user_by_username]: {e}')
            return None

    def get_user_by_id(self, user_id: int):
        """Получение пользователя по имени"""
        query = "SELECT * FROM users WHERE id = ?"
        params = (user_id,)

        try:
            return self.curs.execute(query, params).fetchone()
        except Exception as e:
            print(f'ERROR[get_user_by_username]: {e}')
            return None

    def check_worker(self, id: int):
        """Проверка на работника"""
        query = "SELECT * FROM workers WHERE id = ?"
        params = (id,)

        try:
            result = self.curs.execute(query, params).fetchall()
        except Exception as e:
            print(f'ERROR[check_worker]: {e}')
            result = []

        return bool(len(result))

    # ==================================Пользователи
    # ПОРАВИТЬ В БУДУЩЕМ

    def add_user(self, user_id: int, username: str, refer: int):
        """Добавление юзера"""
        query = (
            'INSERT INTO users(id, username, refer, count_sub, count_days, pay_money, balance) '
            'VALUES(?, ?, ?, 0, 0, 0, 0)'
        )
        params = (user_id, username, refer)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_user]: {e}')
            return False

    def del_user(self, id: int):
        """Удаление юзера"""
        query = "DELETE FROM users WHERE id = ?"
        params = (id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[del_user]: {e}')
            return False

    def get_days(self, id: int):
        """Получить количество оставшихся дней юзера"""
        query = "SELECT count_days FROM users WHERE id = ?"
        params = (id,)

        try:
            return int(self.curs.execute(query, params).fetchone()[0])
        except Exception as e:
            print(f'ERROR[get_days]: {e}')
            return None

    def get_referals(self, id: int):
        """Получить рефералов юзера"""
        query = "SELECT * FROM users WHERE refer = ?"
        params = (id,)

        try:
            return self.curs.execute(query, params).fetchall()
        except Exception as e:
            print(f'ERROR[get_referals]: {e}')
            return []

    def get_pay_money(self, id: int):
        """Получить потраченную сумму юзера"""
        query = "SELECT pay_money FROM users WHERE id = ?"
        params = (id,)

        try:
            return int(self.curs.execute(query, params).fetchone()[0])
        except Exception as e:
            print(f'ERROR[get_pay_money]: {e}')
            return None

    def get_balance(self, id: int):
        """Получаем баланс юзера"""
        query = "SELECT balance FROM users WHERE id = ?"
        params = (id,)
        try:
            return int(self.curs.execute(query, params).fetchone()[0])
        except Exception as e:
            print(f'ERROR[get_balance]: {e}')
            return None

    def add_days(self, id: int, count: int):
        """Добавлить дни юзеру"""
        current_days = self.get_days(id)
        if current_days is None:
            return False

        query = "UPDATE users SET count_days = ? WHERE id = ?"
        params = (current_days + count, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_days]: {e}')
            return False

    def minus_days(self, id: int, count: int):
        """Убавить дни юзеру"""
        current_days = self.get_days(id)
        if current_days is None:
            return False

        query = "UPDATE users SET count_days = ? WHERE id = ?"
        params = (current_days - count, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[minus_days]: {e}')
            return False

    def add_count_sub(self, id: int):
        """Добавить покупку юзеру"""
        current_days = self.get_days(id)
        if current_days is None:
            return False

        query = "UPDATE users SET count_sub = ? WHERE id = ?"
        params = (current_days + 1, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_count_sub]: {e}')
            return False

    def get_all_users(self):
        """Получить список всех пользователей"""
        try:
            return self.curs.execute("SELECT * FROM users LIMIT ? OFFSET ?",
                                     (limit, (page - 1) * limit)).fetchall()
        except Exception as e:
            print(f'ERROR[get_all_users]: {e}')
            return []

    
    def get_all_users(self, limit = 10, page = 1, filter: Literal['', 'by_date_old'] = ''):
        """Получить список всех пользователей"""
        try:
            return self.curs.execute(
                "SELECT * FROM users "
                f"ORDER BY created_at {'ASC' if filter == 'by_date_old' else 'DESC'} "
                "LIMIT ? OFFSET ? ",
                (limit, (page - 1) * limit)
            ).fetchall()
          
        except Exception as e:
            print(f'ERROR[get_all_users]: {e}')
            return []

    def get_users_count(self):
        try:
            return len(self.curs.execute("SELECT * FROM users").fetchall())
        except Exception as e:
            print(f'ERROR[get_users_count]: {e}')
            return 0

    def get_users_with_sub(self):
        """Получить список пользователей с активной подпиской"""
        try:
            return self.curs.execute(
                "SELECT * FROM users WHERE count_days > 0").fetchall()
        except Exception as e:
            print(f'ERROR[get_users_with_sub]: {e}')
            return []

    def get_users_without_sub(self):
        """Получить список бесплатников"""
        try:
            return self.curs.execute(
                "SELECT * FROM users WHERE count_days = 0").fetchall()
        except Exception as e:
            print(f'ERROR[get_users_without_sub]: {e}')
            return []

    def get_users_with_more_pay(self):
        """Получить список пользователей с более 1 покупкой"""
        try:
            return self.curs.execute(
                "SELECT * FROM users WHERE count_sub > 1").fetchall()
        except Exception as e:
            print(f'ERROR[get_users_with_more_pay]: {e}')
            return []

# Базовые значения пользователя
    def add_base_table(self):
        """Добавить нужные столбцы"""
        try:
            self.curs.execute(
                """
                CREATE TABLE `calc_user_settings_temp` (
                `id` integer not null primary key,
                `created_at` datetime not null default CURRENT_TIMESTAMP,
                `base_deposit` FLOAT NULL,
                `base_risk_percent` FLOAT NULL,
                `base_currency` VARCHAR(10) NULL,
                `uses_count` INTEGER DEFAULT(100),
                `take_profit_to_show` VARCHAR(3) DEFAULT('345'),
                `market` VARCHAR(20) DEFAULT('crypto'),
                `lang` VARCHAR(5) NOT NULL DEFAULT 'ru'
                );
                """
            )

            self.curs.execute(
                """
                INSERT INTO calc_user_settings_temp (id, created_at, base_deposit, base_risk_percent, base_currency, lang)
                SELECT id, created_at, base_deposit, base_risk_percent, base_currency, lang
                FROM calc_user_settings;
                """
            )
            self.curs.execute(
                """
                DROP TABLE calc_user_settings;
                """
            )
            self.curs.execute(
                """
                ALTER TABLE calc_user_settings_temp RENAME TO calc_user_settings;
                """
            )

            self.connection.commit()
        except Exception as e:
            print(f'ERROR[add_base_table]: {e}')

    def get_user_base(self, id: int) -> dict[BASE_VALUE_TYPE, Any]:
        """Получить значения для автозаполнения пользователя"""
        query = 'SELECT base_deposit, base_risk_percent, base_currency FROM calc_user_settings WHERE id = ?'
        params = (id,)
        try:
            res = self.curs.execute(query, params).fetchone()
            return {
                'base_deposit': res[0],
                'base_risk_percent': res[1],
                'base_currency': res[2]
            }
        except Exception as e:
            print(f'ERROR[get_user_base]: {e}')
            return {
                'base_deposit': None,
                'base_risk_percent': None,
                'base_currency': None
            }

    def set_user_base(self, user_id: int, type: BASE_VALUE_TYPE, value: float):
        """Установить значения для автозаполения пользователя"""
        value = round(value, 2)
        query = f'INSERT INTO calc_user_settings ({type}, id) VALUES (?, ?) ON CONFLICT (id) DO UPDATE SET {type} = ?'
        params = (value, user_id, value)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_base]: {e}')
            return False

    def set_user_currency(self, user_id: int, value: str):
        """Установить значения для автозаполения пользователя"""
        query = f'UPDATE calc_user_settings SET base_currency = ? WHERE id = ?'
        params = (value, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_currency]: {e}')
            return False

    def get_user_lang(self, user_id: int) -> Optional[LANGUAGES_TYPE]:
        """Получить язык пользователя"""
        query = 'SELECT lang FROM calc_user_settings WHERE id = ?'
        params = (user_id,)
        try:
            data = self.curs.execute(query, params).fetchone()[0]
            return data
        except Exception as e:
            print(f'ERROR[get_user_lang]: {e}')
            return None

    def set_user_lang(self, user_id: int, lang: LANGUAGES_TYPE):
        """Установить язык пользователя"""
        if len(lang) > 5:
            return False

        query = "INSERT INTO calc_user_settings (lang, id) VALUES (?, ?) ON CONFLICT (id) DO UPDATE SET lang = ?"
        params = (lang, user_id, lang)
        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_user_lang]: {e}')
            return False

    def get_calculator_users_id(self) -> list[int]:
        """Получить всех пользователей Калькулятора Бота"""
        query = 'SELECT id FROM calc_user_settings'

        try:
            return self.curs.execute(query).fetchall()
        except Exception as e:
            print(f'ERROR[get_calculator_users_id]: {e}')
            return []

    def delete_calculator_user(self, user_id: int):
        """Удалить пользователя из калькулятора"""
        query = "DELETE FROM calc_user_settings WHERE id = ?"
        params = (user_id,)
        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[delete_calculator_user]: {e}')
            return False

    def get_calculator_uses_count(self, user_id: int) -> int | None:
        """Получить количество использований калькулятора пользователем"""
        query = 'SELECT uses_count FROM calc_user_settings WHERE id = ?'
        params = (user_id,)
        try:
            data = self.curs.execute(query, params).fetchone()[0]
            return data
        except Exception as e:
            print(f'ERROR[get_calculator_uses_count]: {e}')
            return None

    def minus_calculator_uses_count(self, user_id: int):
        """Минус 1 к значению использований у пользователя"""
        query = "UPDATE calc_user_settings SET uses_count = ? WHERE id = ?"
        uses_count = self.get_calculator_uses_count(user_id) or 1
        params = (uses_count - 1, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[minus_calculator_uses_count]: {e}')
            return False

        pass

    def get_calculator_tp_show(self, user_id: int):
        """Получить коэфициенты тейк профит на показ"""
        query = 'SELECT take_profit_to_show FROM calc_user_settings WHERE id = ?'
        params = (user_id,)
        try:
            data = self.curs.execute(query, params).fetchone()[0]
            return data
        except Exception as e:
            print(f'ERROR[get_calculator_tp_show]: {e}')
            return None

    def set_calculator_tp_show(self, user_id: int, tp: str):
        """Установить коэфициенты тейк профит на показ"""
        query = "UPDATE calc_user_settings SET take_profit_to_show = ? WHERE id = ?"
        params = (tp, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculator_tp_show]: {e}')
            return False

    def get_calculator_user_market(self, user_id: int) -> MARKETS_TYPE | None:
        """Получить рынок пользователя"""
        query = 'SELECT market FROM calc_user_settings WHERE id = ?'
        params = (user_id,)
        try:
            data = self.curs.execute(query, params).fetchone()[0]
            return data
        except Exception as e:
            print(f'ERROR[get_calculator_user_market]: {e}')
            return None

    def set_calculator_user_market(self, user_id: int, market: MARKETS_TYPE):
        """Установить рынок пользователя"""
        query = "UPDATE calc_user_settings SET market = ? WHERE id = ?"
        params = (market, user_id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[set_calculator_user_market]: {e}')
            return False

    # ================================= Рабочий персонал
    # Гл.админ

    def add_worker(self, id: int, username: str, role):
        """Добваление работника (1 = админ, 2 = редактор)"""
        self.del_user(id)
        query = "INSERT INTO workers(id, username, role) VALUES(?, ?, ?)"
        params = (id, username, role)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[add_worker]: {e}')
            return False

    def del_worker(self, id: int):
        """Удаление работника"""
        try:
            self.curs.execute(f"DELETE FROM workers WHERE id = ?", (id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[del_worker]: {e}')
            return False

    def get_all_global_admins(self) -> list[Any]:
        """Получить всех глобальных админов"""
        try:
            return self.curs.execute("SELECT id FROM workers WHERE role = 1").fetchall()
        except Exception as e:
            print(f'ERROR[get_all_global_admins]: {e}')
            return []

# Обычный админ
    def get_redactors(self):
        """Получить всех редакторов"""
        try:
            return self.curs.execute("SELECT * FROM workers WHERE role = 2").fetchall()
        except Exception as e:
            print(f'ERROR[get_all_global_admins]: {e}')
            return []

# Тех. поддержка
    def get_support(self):
        """Получение тех. поддержки"""
        try:
            res = self.curs.execute(
                f"SELECT * FROM workers WHERE role = 3").fetchall()
        except Exception as e:
            print(f'ERROR[get_support]: {e}')
            res = []
        return res

    def update_sup(self, username):
        """Изменение тех. поддержки"""
        try:
            self.curs.execute(f"DELETE FROM workers WHERE role = 3")
            self.connection.commit()
            self.curs.execute(
                f"INSERT INTO workers(id, username, role) VALUES(0, ?, 3)", (username,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[update_sup]: {e}')
            return False

    # Получаем список всех работников
    def get_all_workes(self):
        """Получить всех работников"""
        try:
            return self.curs.execute(f"SELECT * FROM workers").fetchall()
        except Exception as e:
            print(f'ERROR[get_all_workes]: {e}')
            return []

    def get_role(self, id) -> int:
        """Узнать роль работника"""
        query = "SELECT role FROM workers WHERE id = ?"
        params = (id,)

        try:
            return self.curs.execute(query, params).fetchone()[0]
        except Exception as e:
            print(f'ERROR[get_role]: {e}')
            return 3

    # ================================ Отложенные посты
    def _data_to_post(self, data: list):
        open_price, stop_loss, name, ticker = data[6], data[7], data[8], data[9]
        details = None

        if (
            open_price is None or
            stop_loss is None or
            name is None or
            ticker is None
        ):
            details = PostDetails(
                name=name,
                open_price=open_price,
                stop_loss=stop_loss,
                ticker=ticker
            )

        return Post(
            id=data[0],
            content=data[1],
            mes_type=data[2],
            media=data[3],
            direct=data[4],
            date_time=data[5],
            details=details
        )

    def add_fut_post(self, post: Post, kind: str):
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
            INSERT INTO posts (content, mes_type, media, direct, date_time, open_price, stop_loss, name, ticker)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (post.content, post.mes_type, post.media, post.direct, post.date_time, *details)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f'ERROR[add_fut_post]: {e}')
            return False

    def del_fut_post(self, post_id):
        """Удалить отложенный пост"""
        try:
            self.curs.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[del_fut_post]: {e}')
            return False

    def get_fut_all_posts(self) -> list[Post]:
        """Получение отложенных постов"""
        query = (
            'SELECT id, content, mes_type, media, direct, '
            'date_time, open_price, stop_loss, name, ticker FROM posts'
        )

        try:
            data = self.curs.execute(query).fetchall()

            return list(map(lambda el: self._data_to_post(el), data))
        except Exception as e:
            print(f'ERROR[get_fut_all_posts]: {e}')
            return []

    def get_fut_post(self, id: int):
        """Получить отложенный пост по id"""
        query = (
            'SELECT id, content, mes_type, media, direct, '
            'date_time, open_price, stop_loss, name, ticker FROM posts WHERE id = ?'
        )
        params = (id,)

        try:
            data = self.curs.execute(query, params).fetchone()

            return self._data_to_post(data) if (data is not None) else None
        except Exception as e:
            print(f'ERROR[get_fut_post]: {e}')
            return None

    # ================================ Изменние КИВИ ТОКЕНА И т.д.
    def update_qiwi_token(self, token):
        self.curs.execute(
            f"UPDATE pay set value = {token} WHERE name = 'qiwi_token'")
        self.connection.commit()
        print('Изменён qiwi токен!!!')

    # ================================= OTHER

    def get_all_others(self):
        """Получить все текста"""
        try:
            res = self.curs.execute(f"SELECT * FROM other").fetchall()
        except:
            res = []

        return res

    def get_other_by_name(self, name: str) -> str | None:
        """Получить конкретный текста"""
        try:
            return self.curs.execute(
                f"SELECT text FROM other WHERE name = ?", (name,)).fetchone()[0]
        except:
            return None

    def update_other(self, name: str, text: str):
        other = self.get_other_by_name(name)
        try:
            if other == None:
                self.curs.execute(
                    'INSERT INTO other(text, name) VALUES(?, ?)', (text, name,))
            else:
                self.curs.execute(
                    'UPDATE other set text = ? WHERE name = ?', (text, name,))
            self.connection.commit()
            print(f'Изменение {name} - {text}')
        except:
            print(f'[ERROR]: update other {name} - {text}')

    # ================ Фьючерсы

    def update_future(self, name, step, price_step):
        self.curs.execute(f"UPDATE future set step = ?, price_step = ? WHERE name = ?",
                          (step, price_step, name.lower(),))
        self.connection.commit()

    def check_future(self, name):
        name = name.lower()
        result = self.curs.execute(
            "SELECT * FROM future WHERE name = ?", (name,)).fetchall()
        return bool(len(result))

    def get_all_future(self):
        result = self.curs.execute("SELECT * FROM future").fetchall()
        return result

    def get_future(self, name: str):
        name = name.lower()
        try:
            return self.curs.execute(
                f"SELECT * FROM future WHERE name = '{name}'").fetchone()
        except:
            return None

    def add_future(self, name: str, step: int, price_step: float):
        try:
            self.curs.execute(f"INSERT INTO future (name, step, price_step) VALUES (?, ?, ?)",
                              (name.lower(), step, price_step))
            self.connection.commit()
        except Exception as e:
            print(e)

    # Уроки
    def add_count_les(self, id: int):
        query = "UPDATE users set count_les = ? WHERE id = ?"
        count = self.get_count_les(id) + 1
        params = (count, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f'ERROR[users_add_les]: {e}')
            return False

    def get_count_les(self, id: int):
        query = "SELECT count_les FROM users WHERE id = ?"
        params = (id,)
        try:
            res = self.curs.execute(query, params).fetchone()[0]
            if res == None:
                return 1
            else:
                return res
        except Exception as e:
            print(f'ERROR[get_count_les]: {e}')
            return 1

# ======================= // ANCHOR Новости
    def add_news(self, text):
        self.curs.execute(f"INSERT INTO news(text) VALUES(?)", (text,))
        print(f'[BART SCRIPT]: Добавлена новость в базу \n{text}')
        self.connection.commit()

    def check_news(self, text):
        result = self.curs.execute(
            "SELECT * FROM news WHERE text = ?", (text,)).fetchall()
        return bool(len(result))

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

    def check_ban_user(self, user_id):
        """Проверка на бан"""
        query = "SELECT ban FROM users WHERE id = ? and ban IS NOT NULL"
        params = (user_id,)

        try:
            result = self.curs.execute(query, params).fetchone()
            return (result is not None) and (len(result) == 1) and (result[0] is not None)
        except Exception as e:
            print(f'ERROR[check_ban_user]: {e}')
            return False

    # Получить пользователей без бана
    def get_users_no_ban(self):
        res = self.curs.execute(
            f"SELECT * FROM users WHERE ban IS NULL").fetchall()
        return res

    # Получить забаненных пользователей
    def get_ban_users(self):
        res = self.curs.execute(
            f"SELECT * FROM users WHERE ban IS NOT NULL").fetchall()
        return res

    # Установить статус забанненого / незабанненого пользователя
    def set_user_ban_status(self, user_id, status):
        self.curs.execute(f"UPDATE users set ban = ? WHERE id = ?",
                          (status, user_id,))
        self.connection.commit()
        print(
            f'Обновили статус в status [{status}] пользователя user_id [{user_id}]')

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

    def get_subsribe_more1_users(self, today):
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

    def del_debug_user(self, user_id):
        self.curs.execute(f"DELETE FROM users WHERE username = ?", (user_id,))
        print(f'Удален тестовый пользователь {user_id}')
        self.connection.commit()

# ======================= // Редактирование текстов

    def get_list_texts(self):
        res = self.curs.execute(f"SELECT * FROM bot_texts").fetchall()
        return res

    def get_single_text(self, label):
        res = self.curs.execute(
            "SELECT * FROM bot_texts WHERE label = ?", (label,)).fetchone()
        return res

    def save_bot_text_by_id(self, text_id, content):
        self.curs.execute(f"UPDATE bot_texts set content = ? WHERE id = ?",
                          (content, text_id,))
        self.connection.commit()
        print(f'Обновили текст bot_text под  text_id [{text_id}]')

# ======================= // Отсутствующие функции
    def get_prices(self, active):
        res = self.curs.execute(
            f"SELECT * FROM prices WHERE active = ?", (active,)).fetchall()
        return res


db = Database('4p_bot.db')
