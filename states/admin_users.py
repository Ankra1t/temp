from telebot.asyncio_handler_backends import State, StatesGroup


class AdminUsersState(StatesGroup):
    client_search = State()

    subscribe_days = State()

    trial_subscribe_days_get_days = State()
