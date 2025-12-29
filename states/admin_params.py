from telebot.asyncio_handler_backends import State, StatesGroup


class AdminParamsState(StatesGroup):
    text = State()

    trailing_stop = State()


class AdminMainState(StatesGroup):
    turnover = State()
    notification = State()
