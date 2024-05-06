from telebot.handler_backends import State, StatesGroup


class StatsState(StatesGroup):
    loss = State()
    sum = State()

    freeze = State()

    add_image = State()
