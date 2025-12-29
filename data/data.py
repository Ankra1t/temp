import json
import sqlite3

from models import MARKETS_TYPE, Exchange


class Data:
    def __init__(self):
        self.connection = sqlite3.connect(
            'data/data.db', check_same_thread=False
        )
        self.curs = self.connection.cursor()

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

    def getUserStop(self, tgId: int) -> str | None:
        try:
            data = self.curs.execute(
                'SELECT stop FROM Users WHERE id = ?', (tgId,)
            ).fetchone()
            if data is None:
                return None

            return data[0]
        except Exception as e:
            print(e)
            return None

    def setUserStop(self, tgId: int, stop: str):
        self.addUser(tgId)
        try:
            self.curs.execute(
                'UPDATE Users SET stop = ? WHERE id = ?', (stop, tgId)
            )
            self.connection.commit()

            return True
        except Exception as e:
            print(e)
            return False

    def getStyleChange(self, tgId: int) -> bool:
        self.addUser(tgId)
        try:
            data = self.curs.execute(
                "SELECT style_change FROM Users WHERE id = ?",
                (tgId,)
            ).fetchone()

            if data is None:
                return False

            return data[0] == 1
        except Exception as e:
            print(e)
            return False

    def switchStyleChange(self, tgId: int):
        prev_value = self.getStyleChange(tgId)
        try:
            self.curs.execute(
                'UPDATE Users SET style_change = ? WHERE id = ?',
                (not prev_value, tgId)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def setUserFirstMarket(self, tgId: int, market: MARKETS_TYPE):
        self.addUser(tgId)
        try:
            self.curs.execute(
                'UPDATE Users SET first_market = ? WHERE id = ?',
                (market, tgId)
            )
            self.connection.commit()

            return True
        except Exception as e:
            print(e)
            return False

    def getUserAtrSettings(self, tgId: int) -> tuple[bool, str]:
        default = (False, '')
        try:
            data = self.curs.execute(
                'SELECT is_auto_atr, atr_bars FROM Users WHERE id = ?', (tgId,)
            ).fetchone()
            if data is None:
                return default

            return (data[0], data[1])
        except Exception as e:
            print(e)
            return default

    def setUserAtrSettings(self, tgId: int, value: tuple[bool, str]):
        self.addUser(tgId)
        try:
            self.curs.execute(
                'UPDATE Users SET is_auto_atr = ?, atr_bars = ? WHERE id = ?',
                (*value, tgId)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

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

    # Calc
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

    def updateSendSettings(self, name: str, value: str | None):
        try:
            self.curs.execute("""
                UPDATE SendSettings SET value = ? WHERE name = ?;
            """, (value, name)
            )
            self.connection.commit()

            return True
        except Exception as e:
            print(e)
            return False

    def getSendSettings(self, name: str) -> str | None:
        try:
            data = self.curs.execute("""
                SELECT value FROM SendSettings WHERE name = ?;
            """, (name,)
            ).fetchone()

            if data is None:
                return

            return data[0]
        except Exception as e:
            print(e)
            return


liteDb = Data()
