from telebot.states import State, StatesGroup


class UserAccountState(StatesGroup):
    password = State()

    nickname = State()
