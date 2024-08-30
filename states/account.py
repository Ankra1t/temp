from telebot.asyncio_handler_backends import State, StatesGroup


class UserAccountState(StatesGroup):
    password = State()

    nickname = State()
