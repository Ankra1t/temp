from telebot.asyncio_handler_backends import State, StatesGroup


class TariffState(StatesGroup):
    email = State()
