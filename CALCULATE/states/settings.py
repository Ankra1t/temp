from telebot.handler_backends import State, StatesGroup


class SettingsState(StatesGroup):
    deposit = State()
    risk_percent = State()
    day_risk = State()
    currency = State()

    round_count = State()

    summury_profit = State()
    splitting = State()
