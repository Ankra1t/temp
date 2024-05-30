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

    def addUser(self, userId: int):
        try:
            data = self.curs.execute(
                "SELECT * FROM Users WHERE id = ?", (userId,)).fetchone()
            if data is not None:
                return

            self.curs.execute("INSERT INTO Users (id) VALUES (?)", (userId,))
            self.connection.commit()
        except Exception as e:
            print(e)

    def getRiskUpdate(self, userId: int) -> bool:
        self.addUser(userId)
        try:
            data = self.curs.execute(
                "SELECT is_risk_update FROM Users WHERE id = ?",
                (userId,)
            ).fetchone()

            if data is None:
                return False

            return data[0] == 1
        except Exception as e:
            print(e)
            return False

    def reverseRiskUpdate(self, userId: int):
        prev_value = self.getRiskUpdate(userId)
        try:
            self.curs.execute(
                'UPDATE Users SET is_risk_update = ? WHERE id = ?',
                (not prev_value, userId)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def setFirstTry(self, userId: int):
        self.addUser(userId)
        try:
            self.curs.execute(
                "UPDATE Users SET first_try = ? WHERE id = ?", (True, userId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def addStartCalcCount(self, userId: int):
        self.addUser(userId)
        try:
            data = self.curs.execute(
                "SELECT start_calc_count FROM Users WHERE id = ?", (userId,)
            ).fetchone()
            data = data[0] if data is not None else 0

            self.curs.execute(
                "UPDATE Users SET start_calc_count = ? WHERE id = ?", (data + 1, userId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def addPagesCount(self, userId: int):
        self.addUser(userId)
        try:
            data = self.curs.execute(
                "SELECT pages_count FROM Users WHERE id = ?", (userId,)
            ).fetchone()
            data = data[0] if data is not None else 0

            self.curs.execute(
                "UPDATE Users SET pages_count = ? WHERE id = ?", (data + 1, userId,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def getFirstTriesCount(self) -> int:
        try:
            data = self.curs.execute("SELECT COUNT(*) FROM Users WHERE first_try = ?", (True,)).fetchone()
            return data[0] if data is not None else 0
        except Exception as e:
            print(e)
            return 0

liteDb = Data()