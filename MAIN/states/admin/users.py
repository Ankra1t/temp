from telebot.handler_backends import State, StatesGroup


class AdminUsersState(StatesGroup):
    client_search = State()

    subscribe_days = State()
