from telebot.handler_backends import State, StatesGroup


class SettingsState(StatesGroup):
    deposit = State()
    risk_percent = State()
    day_risk = State()
    currency = State()

    round_count = State()
    trading_style = State()

    summury_profit = State()
    splitting = State()

    exchange = State()
    fee = State()

    atr_percent = State()

class FirstCalcState(StatesGroup):
    deposit = State()
    risk = State()