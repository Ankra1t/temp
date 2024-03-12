from telebot.handler_backends import State, StatesGroup


class StatsState(StatesGroup):
    loss = State()

    freeze = State()
