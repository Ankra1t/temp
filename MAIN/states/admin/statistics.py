from telebot.handler_backends import State, StatesGroup


class AdminStatisticsState(StatesGroup):
    start_date = State()
    fin_date = State()

    start_date_only = State()
