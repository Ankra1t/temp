from telebot.states import State, StatesGroup


class AdminPostsState(StatesGroup):
    name = State()
