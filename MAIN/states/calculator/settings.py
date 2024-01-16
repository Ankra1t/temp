from telebot.handler_backends import State, StatesGroup


class SettingsState(StatesGroup):
    deposit = State()
    risk_percent = State()
    currency = State()