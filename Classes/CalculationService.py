from telebot import TeleBot

from db_new import Database


class CalculationService():
    def __init__(self, bot: TeleBot, db: Database) -> None:
        self.bot = bot
        self.db = db

    def set_profit(self, stat_id: int, value: float):
        self.db.set_calculation_profit(stat_id, value)
        self.db.set_calculation_in_stat(stat_id, True)

