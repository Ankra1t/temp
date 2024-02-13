from telebot.handler_backends import State, StatesGroup


class AdminWorkersState(StatesGroup):
    add_id = State()

    delete_id = State()

    update_support = State()
