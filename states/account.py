from telebot.states import State, StatesGroup


class UserAccountState(StatesGroup):
    nickname = State()
