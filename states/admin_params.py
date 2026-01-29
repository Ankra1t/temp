from telebot.states import State, StatesGroup


class AdminParamsState(StatesGroup):
    trailing_stop = State()


class AdminMainState(StatesGroup):
    turnover = State()
