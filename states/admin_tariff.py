from telebot.asyncio_handler_backends import State, StatesGroup


class AdminSubsState(StatesGroup):
    user_id_name = State()
