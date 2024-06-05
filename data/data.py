import sqlite3


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
                    start_calc_count INTEGER NOT NULL DEFAULT(0),
                    pages_count INTEGER NOT NULL DEFAULT(0)
                );
			''')
            self.curs.execute('''
                INSERT INTO NewTemp (id, is_risk_update)
                SELECT id, is_risk_update
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

    def createFeeTable(self):
        try:
            #             self.curs.execute("""
            # DROP TABLE Exchanges;
            # """)
            self.curs.execute("""
CREATE TABLE IF NOT EXISTS Exchanges (
    id INTEGER PRIMARY KEY,
    name STRING NOT NULL,
    maker_fee FLOAT NOT NULL,
    taker_fee FLOAT NOT NULL
);
""")
        except Exception as e:
            print(e)

    def addExchange(self, id: int, name: str, maker_fee: float, taker_fee: float):
        try:
            data = self.curs.execute(
                'SELECT * FROM Exchanges WHERE id = ?', (id,)
            ).fetchone()

            if data is None:
                self.curs.execute(
                    'INSERT INTO Exchanges (id, name, maker_fee, taker_fee) VALUES (?, ?, ?, ?)',
                    (id, name, maker_fee, taker_fee)
                )
            else:
                self.curs.execute(
                    'UPDATE Exchanges SET name = ?, maker_fee = ?, taker_fee = ? WHERE id = ?',
                    (name, maker_fee, taker_fee, id)
                )

            self.connection.commit()
        except Exception as e:
            print(e)


liteDb = Data()
liteDb.createFeeTable()
