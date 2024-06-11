import json
import sqlite3

from models import Exchange


class Data:
    def __init__(self):
        self.connection = sqlite3.connect(
            'data/data.db', check_same_thread=False
        )
        self.curs = self.connection.cursor()

    def createUsersTable(self):
        try:
            self.curs.execute('''
                CREATE TABLE NewTemp (
                    id INTEGER PRIMARY KEY,
				    is_risk_update BOOLEAN NOT NULL DEFAULT(FALSE),
				    first_try BOOLEAN NOT NULL DEFAULT(FALSE),
				    first_lang BOOLEAN NOT NULL DEFAULT(FALSE),
                    start_calc_count INTEGER NOT NULL DEFAULT(0),
                    pages_count INTEGER NOT NULL DEFAULT(0),
                    exchange STRING,
                    fee FLOAT
                );
			''')
            self.curs.execute('''
                INSERT INTO NewTemp (id, is_risk_update, first_try, start_calc_count, pages_count, exchange, fee)
                SELECT id, is_risk_update, first_try, start_calc_count, pages_count, exchange, fee
                FROM Users;
			''')
            self.curs.execute('''
                DROP TABLE Users;
			''')
            self.curs.execute('''
                ALTER TABLE NewTemp RENAME TO Users;
			''')
            self.connection.commit()
        except Exception as e:
            print(e)

    def addUser(self, tgId: int):
        try:
            data = self.curs.execute(
                "SELECT * FROM Users WHERE id = ?", (tgId,)).fetchone()
            if data is not None:
                return

            self.curs.execute("INSERT INTO Users (id) VALUES (?)", (tgId,))
            self.connection.commit()
        except Exception as e:
            print(e)

    def getRiskUpdate(self, tgId: int) -> bool:
        self.addUser(tgId)
        try:
            data = self.curs.execute(
                "SELECT is_risk_update FROM Users WHERE id = ?",
                (tgId,)
            ).fetchone()

            if data is None:
                return False

            return data[0] == 1
        except Exception as e:
            print(e)
            return False

    def reverseRiskUpdate(self, tgId: int):
        prev_value = self.getRiskUpdate(tgId)
        try:
            self.curs.execute(
                'UPDATE Users SET is_risk_update = ? WHERE id = ?',
                (not prev_value, tgId)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def setFirstTry(self, tgId: int):
        self.addUser(tgId)
        try:
            self.curs.execute(
                "UPDATE Users SET first_try = ? WHERE id = ?", (True, tgId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def addStartCalcCount(self, tgId: int):
        self.addUser(tgId)
        try:
            data = self.curs.execute(
                "SELECT start_calc_count FROM Users WHERE id = ?", (tgId,)
            ).fetchone()
            data = data[0] if data is not None else 0

            self.curs.execute(
                "UPDATE Users SET start_calc_count = ? WHERE id = ?", (
                    data + 1, tgId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def addPagesCount(self, tgId: int):
        self.addUser(tgId)
        try:
            data = self.curs.execute(
                "SELECT pages_count FROM Users WHERE id = ?", (tgId,)
            ).fetchone()
            data = data[0] if data is not None else 0

            self.curs.execute(
                "UPDATE Users SET pages_count = ? WHERE id = ?", (
                    data + 1, tgId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def getFirstTriesCount(self) -> int:
        try:
            data = self.curs.execute(
                "SELECT COUNT(*) FROM Users WHERE first_try = ?", (True,)).fetchone()
            return data[0] if data is not None else 0
        except Exception as e:
            print(e)
            return 0

    def getFirstTryUser(self, tgId: int) -> int:
        try:
            data = self.curs.execute(
                "SELECT first_try FROM Users WHERE id = ?", (tgId,)).fetchone()
            return data[0] if data is not None else 0
        except Exception as e:
            print(e)
            return 0

    def getUserExchange(self, tgId: int) -> tuple[str, float] | None:
        try:
            data = self.curs.execute(
                'SELECT exchange, fee from Users WHERE id = ?', (tgId,)
            ).fetchone()

            if data is None or data[0] is None or data[1] is None:
                return None

            return (data[0], data[1])
        except Exception as e:
            print(e)
            return None

    def setUserExchange(self, tgId: int, value: tuple[str | None, float | None]) -> bool:
        self.addUser(tgId)
        try:
            self.curs.execute(
                'UPDATE Users SET exchange = ?, fee = ? WHERE id = ?',
                (*value, tgId,)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def setFirstLang(self, tgId: int):
        self.addUser(tgId)
        try:
            self.curs.execute(
                "UPDATE Users SET first_lang = ? WHERE id = ?", (True, tgId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def getFirstLangsCount(self) -> int:
        try:
            data = self.curs.execute(
                "SELECT COUNT(*) FROM Users WHERE first_lang = ?", (True,)).fetchone()
            return data[0] if data is not None else 0
        except Exception as e:
            print(e)
            return 0

    def getFirstLang(self, tgId: int) -> int:
        try:
            data = self.curs.execute(
                "SELECT first_lang FROM Users WHERE id = ?", (tgId,)).fetchone()
            return data[0] if data is not None else 0
        except Exception as e:
            print(e)
            return 0

    # FEES
    def createFeeTable(self):
        try:
            self.curs.execute("""
DROP TABLE Exchanges;
""")
            self.curs.execute("""
CREATE TABLE IF NOT EXISTS Exchanges (
    id INTEGER PRIMARY KEY,
    name STRING NOT NULL,
    maker_fee FLOAT NOT NULL,
    taker_fee FLOAT NOT NULL,
    fees STRING
);
""")
        except Exception as e:
            print(e)

    def addExchange(self, id: int, name: str, maker_fee: float, taker_fee: float, fees: list[tuple[str, float, float]]):
        try:
            data = self.curs.execute(
                'SELECT id, name, maker_fee, taker_fee, fees FROM Exchanges WHERE id = ?', (
                    id,)
            ).fetchone()

            if len(fees) == 0:
                fees_str = None
            else:
                fees_str = json.dumps(fees)

            if data is None:
                self.curs.execute(
                    'INSERT INTO Exchanges (id, name, maker_fee, taker_fee, fees) VALUES (?, ?, ?, ?, ?)',
                    (id, name, maker_fee, taker_fee, fees_str)
                )
            else:
                self.curs.execute(
                    'UPDATE Exchanges SET name = ?, maker_fee = ?, taker_fee = ?, fees = ? WHERE id = ?',
                    (name, maker_fee, taker_fee, fees_str or data[4], id)
                )

            self.connection.commit()
        except Exception as e:
            print(e)

    def getExchanges(self) -> list[Exchange]:
        try:
            data = self.curs.execute(
                'SELECT id, name, maker_fee, taker_fee, fees FROM Exchanges'
            ).fetchall()

            if data is None:
                return []

            return [
                Exchange(
                    id=el[0],
                    name=el[1],
                    maker_fee=el[2],
                    taker_fee=el[3],
                    fees=json.loads(el[4]) if el[4] is not None else []
                ) for el in data
            ]
        except Exception as e:
            print(e)
            return []

    def getExchangeByName(self, name: str) -> Exchange | None:
        try:
            data = self.curs.execute(
                'SELECT id, name, maker_fee, taker_fee, fees FROM Exchanges WHERE name = ?',
                (name,)
            ).fetchone()

            if data is None:
                return None

            return Exchange(
                id=data[0],
                name=data[1],
                maker_fee=data[2],
                taker_fee=data[3],
                fees=json.loads(data[4]) if data[4] is not None else []
            )

        except Exception as e:
            print(e)
            return None

    def createCalcTable(self):
        try:
            #             self.curs.execute("""
            # DROP TABLE Exchanges;
            # """)
            self.curs.execute("""
CREATE TABLE IF NOT EXISTS Calcs (
    id INTEGER PRIMARY KEY,
    exchange STRING,
    fee FLOAT
);
""")
        except Exception as e:
            print(e)

    def addCalc(self, id: int, name: str, fee: float):
        try:
            self.curs.execute(
                'INSERT INTO Calcs (id, exchange, fee) VALUES (?, ?, ?)',
                (id, name, fee)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def getCalc(self, id: int) -> None | tuple[str, float]:
        try:
            data = self.curs.execute(
                'SELECT exchange, fee FROM Calcs WHERE id = ?', (id,)).fetchone()
            if data is None:
                return None

            return data[0], data[1]
        except Exception as e:
            print(e)
            return None

    def createTonStorage(self):
        try:
            self.curs.execute("""
CREATE TABLE IF NOT EXISTS TonStorage (
    key STRING PRIMARY KEY,
    value STRING NOT NULL
);
""")
        except:
            pass

    def setTonStorage(self, key: str, value: str):
        try:
            self.curs.execute(
                'INSERT INTO TonStorage (key, value) VALUES (?, ?)',
                (key, value)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
            pass

    def getTonStorage(self, key: str) -> str | None:
        try:
            data = self.curs.execute(
                'SELECT value FROM TonStorage WHERE key = ?',
                (key,)
            ).fetchone()

            return data[0] if data is not None else None
        except Exception as e:
            print(e)
            return None

    def delTonStorage(self, key: str):
        try:
            self.curs.execute(
                'DELETE FROM TonStorage WHERE key = ?',
                (key)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
            pass

liteDb = Data()
liteDb.createTonStorage()
liteDb.createUsersTable()