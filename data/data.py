import sqlite3


class Data:
    def __init__(self):
        self.connection = sqlite3.connect(
            'data/data.db', check_same_thread=False
        )
        self.curs = self.connection.cursor()

    def createTable(self):
        try:
            self.curs.execute('''
				CREATE TABLE IF NOT EXISTS Users (
				id INTEGER PRIMARY KEY,
				is_risk_update BOOLEAN NOT NULL DEFAULT(FALSE)
				)
			''')
            self.connection.commit()
        except Exception as e:
            print(e)

    def addUser(self, userId: int):
        try:
            self.curs.execute("INSERT INTO Users (id) VALUES (?)", (userId,))
            self.connection.commit()
        except Exception as e:
            print(e)

    def getRiskUpdate(self, userId: int) -> bool:
        try:
            data = self.curs.execute(
                "SELECT is_risk_update FROM Users WHERE id = ?",
                (userId,)
            ).fetchone()

            if data is None:
                self.addUser(userId)
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


liteDb = Data()
