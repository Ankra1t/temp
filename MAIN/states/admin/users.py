from telebot.handler_backends import State, StatesGroup


class AdminUsersState(StatesGroup):
    client_search = State()

    subscribe_username = State()
    subscribe_days = State()

    sub_user_id = State()
    sub_days = State()
    sub_choice = State()

    ban_username = State()
