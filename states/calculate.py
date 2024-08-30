from telebot.asyncio_handler_backends import State, StatesGroup


class CalculateState(StatesGroup):
    deposit = State()
    currency = State()

    trading_style = State()

    risk_percent = State()
    open_price = State()
    stop_loss = State()
    stop_atr = State()

    tool = State()

    max_bar = State()
    min_bar = State()


class ForexCalcState(StatesGroup):
    pair = State()
    pair_price = State()

    val_dep = State()
