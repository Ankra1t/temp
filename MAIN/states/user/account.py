from telebot.handler_backends import State, StatesGroup


class UserAccountState(StatesGroup):
    password = State()
