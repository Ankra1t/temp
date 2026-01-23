from telebot.states import State, StatesGroup


class AdminParamsState(StatesGroup):
    text = State()

    trailing_stop = State()


class AdminMainState(StatesGroup):
    turnover = State()
