from telebot.handler_backends import State, StatesGroup


class CalculateState(StatesGroup):
    deposit = State()
    risk_percent = State()
    open_price = State()
    stop_loss = State()


class FutureCalcState(StatesGroup):
    ticker = State()


class ForexCalcState(StatesGroup):
    pair = State()
    val_dep = State()

    stop_loss = State()
