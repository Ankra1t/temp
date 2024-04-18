from telebot.handler_backends import State, StatesGroup


class CalculateState(StatesGroup):
    deposit = State()
    currency = State()

    trading_style = State()

    risk_percent = State()
    open_price = State()
    stop_loss = State()

    tool = State()


class ForexCalcState(StatesGroup):
    pair = State()
    val_dep = State()
