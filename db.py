from psycopg2.extras import DictCursor, DictRow
import psycopg2
import json
import traceback
from time import sleep

from config_global import DB_PG_HOST, DB_PG_NAME, DB_PG_PASS, DB_PG_PORT, DB_PG_USER
from config_logger import logger

from models import (
    ROLE_TYPE,
    Calculation,
    ForexInfo, Post, PostDetails, Text, UnfinishedCalculation,
    Worker, MARKETS_TYPE,
)


class Database:
    def __init__(self, user: str, password: str, host: str, port: int, database: str):
        self._config = (user, password, host, port, database)
        self._connect()

    def _connect(self):
        user, password, host, port, database = self._config
        try:
            self.connection = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            self.curs = self.connection.cursor(cursor_factory=DictCursor)
        # except Exception as e:
        except:
            # self._log_error(e)
            pass

    def _log_error(self, e: Exception):
        stack = traceback.extract_stack()
        logger.error(f'[db.{stack[-2].name}]: {e}')

        retries = 0
        while not (self.connection and self.connection.closed == 0) and retries < 5:
            self._connect()
            retries += 1
            sleep(1)

    # Пользователи

    # Уроки пользователей

    def add_lesson_count(self, id: int):
        query = 'UPDATE \"BotSettings\" set "lessonCount" = %s WHERE "userId" = %s'
        count = self.get_lesson_count(id) + 1
        params = (count, id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    def get_lesson_count(self, id: int):
        query = 'SELECT "lessonCount" FROM \"BotSettings\" WHERE "userId" = %s'
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()

            if data == None:
                return 1
            else:
                return data['lesson_count']
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return 1

    # Статистика расчётов
    def _data_to_calculations(self, data: DictRow):
        pair = data.get('pair')
        pair_price = data.get('pairPrice')
        cross_prices = data.get('crossPrices')

        forex = None
        if (pair is not None) and (pair_price is not None) and (cross_prices is not None):
            pairs = str(pair).split('/')
            forex = ForexInfo(
                pair=(pairs[0], pairs[1]),
                price=pair_price,
                cross_prices=json.loads(cross_prices)
            )

        split_values = data.get('splitValues')
        if split_values is not None and len(split_values) == 0:
            split_values = None

        return Calculation(
            id=data.get('id'),
            userId=data.get('userId'),
            profit=data.get('profit'),
            inStat=data.get('inStat'),
            statDt=data.get('statDt'),
            deposit=data.get('deposit'),
            riskValue=data.get('riskValue'),
            openPrice=data.get('openPrice'),
            stopLoss=data.get('stopLoss'),
            roundCount=data.get('roundCount'),
            currency=data.get('currency'),
            tradingStyle=data.get('tradingStyle'),
            market=data.get('market'),
            tpRatio=data.get('tpRatio'),
            splitValues=split_values,
            forexInfo=forex,
            tool=data.get('tool'),
            tradingType=data.get('tradingType'),
            isFromDeposit=data.get('isFromDeposit'),
            createdAt=str(data.get('createdAt')),
            status=data.get('status'),
        )

    def add_calculation(self, value: Calculation):
        query = (
            'INSERT INTO "Calculation" ("userId", deposit, "riskValue", "openPrice", "stopLoss", "roundCount", '
            'currency, "tradingStyle", market, "tpRatio", "splitValues", pair, "pairPrice", "crossPrices", tool, "tradingType") '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id'
        )

        pair_price = pair = cross_prices = None
        if value.forexInfo is not None:
            pair_price = value.forexInfo.price
            pair = '/'.join(value.forexInfo.pair)
            cross_prices = json.dumps(value.forexInfo.cross_prices)

        params = (
            value.userId, value.deposit, value.riskValue, value.openPrice, value.stopLoss,
            value.roundCount, value.currency, value.tradingStyle, value.market,
            value.tpRatio, value.splitValues, pair, pair_price, cross_prices, value.tool,
            value.tradingType
        )

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            if data is None:
                raise Exception('Ошибка с записью в БД')

            self.connection.commit()
            return int(data.get('id'))
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    def change_calculation_style(self, id: int, value: str | None):
        query = 'UPDATE "Calculation" SET "tradingStyle" = %s WHERE id = %s'
        params = (value, id)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    def delete_calculation(self, id: int):
        query = 'DELETE FROM "Calculation" WHERE id = %s'
        params = id,

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    def get_calculations_by_user(
        self,
        user_id: int,
        saved: bool | None = None,
        market: MARKETS_TYPE | None = None
    ) -> list[Calculation]:
        query = 'SELECT * FROM "Calculation" WHERE "userId" = %s'
        params = (user_id,)

        if saved is not None:
            query += ' AND "inStat" = %s'
            params = (*params, True)

        if market is not None:
            query += ' AND market = %s'
            params = (*params, market)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_calculations(el), data))
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return []

    # Работники
    def _data_to_worker(self, data: DictRow):
        return Worker(
            id=data.get('id'),
            tg_id=data.get('tgId') or 0,
            username=data.get('tgUsername') or '',
            role=data.get('role')
        )

    WORKER_QUERY = (
        'SELECT w."userId" as id, w.role, u."tgId", u."tgUsername" FROM "Admin" as w '
        'LEFT JOIN \"User\" as u ON u.id = w."userId" '
    )

    def add_worker(self, id: int, role: ROLE_TYPE):
        """Добваление работника (1 = админ, 2 = редактор)"""
        query = 'INSERT INTO "Admin"("userId", role) VALUES(%s, %s)'
        params = (id, role)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    def del_worker(self, id: int):
        """Удаление работника"""
        query = 'DELETE FROM "Admin" WHERE "userId" = %s'
        params = (id,)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
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
            self._log_error(e)
            self.connection.rollback()
            return []

    def get_support_name(self) -> str:
        """Получение тех. поддержки"""
        return 'calcsup'

    def update_support(self, id: int):
        """Изменение тех. поддержки"""
        query = 'UPDATE "Admin" SET "userId" = %s WHERE role = %s'
        params = id, 'SUPPORT'

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    def get_worker_role(self, id: int) -> ROLE_TYPE | None:
        """Узнать роль работника"""
        query = 'SELECT role FROM "Admin" WHERE "userId" = %s'
        params = (id,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return data.get('role') if (data is not None) else None
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return None

    # Аутентификация
    def get_access_token(self) -> str | None:
        query = 'SELECT value FROM "AccessOption" WHERE name = %s'
        params = ('tg-api-key',)

        try:
            self.curs.execute(query, params)
            res = self.curs.fetchone()
            return res['value'] if res is not None else None
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return None

    # Посты
    def _data_to_post(self, data: DictRow):
        open_price, stop_loss, name, ticker = (
            data.get('openPrice'),
            data.get('stopLoss'),
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
            mes_type=data.get('messageType'),
            media=data.get('media'),
            direct=data.get('direct') or '',
            date_time=data.get('sendDt'),
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
            INSERT INTO BotPost (message, "messageType", "mediaId", direct, "sendDt", "openPrice", stopLoss, name, ticker)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (post.content, post.mes_type, post.media,
                  post.direct, post.date_time, *details)

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
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
            self._log_error(e)
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
            self._log_error(e)
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
            self._log_error(e)
            self.connection.rollback()
            return None

    # Тексты
    def _data_to_text(self, data: DictRow):
        return Text(
            id=data.get('id'),
            name=data.get('name'),
            message=data.get('message') or '',
            message_type=data.get('messageType') or 'text',
            media_id=data.get('mediaId') or '',
            media_id_en=data.get('mediaIdEn')
        )

    def get_texts(self) -> list[Text]:
        query = 'SELECT * FROM "BotText"'

        try:
            self.curs.execute(query)
            data = self.curs.fetchall()
            return list(map(lambda el: self._data_to_text(el), data)) if (data is not None) else []
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return []

    def get_text_by_name(self, name: str):
        query = 'SELECT * FROM "BotText" WHERE name = %s'
        params = (name,)

        try:
            self.curs.execute(query, params)
            data = self.curs.fetchone()
            return self._data_to_text(data) if (data is not None) else None
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return None

    def update_text(self, name: str, text: str):
        mes_type = 'text'
        check_text = self.get_text_by_name(name)

        try:
            if check_text is None:
                query = 'INSERT INTO "BotText"(message, "messageType", name) VALUES(%s, %s, %s)'
            else:
                query = 'UPDATE "BotText" SET message = %s, "messageType" = %s WHERE name = %s'

            params = (text, mes_type, name)

            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False

    # Незавершённые расчёты

    def add_unfinished_calc(self, value: UnfinishedCalculation):
        query = 'INSERT INTO "UnfinishedCalc" '
        query += '("userId", "openPrice", tool, pair, "pairPrice", "crossPrices", "tradingStyle", '
        query += '"riskValue", "updateRiskRate", "isRiskPercent", deposit, currency, "lastValues") '
        query += 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        pair_price = pair = cross_prices = None
        if value.forex is not None:
            pair_price = value.forex.price
            pair = '/'.join(value.forex.pair)
            cross_prices = json.dumps(value.forex.cross_prices)

        params = (
            value.user_id, value.open_price, value.tool, pair, pair_price, cross_prices, value.trading_style,
            value.risk_value, value.update_risk_rate, value.is_risk_percent, value.deposit, value.currency,
            value.last_values
        )

        try:
            self.curs.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self._log_error(e)
            self.connection.rollback()
            return False


db = Database(DB_PG_USER, DB_PG_PASS, DB_PG_HOST, DB_PG_PORT, DB_PG_NAME)
