from telebot.states import State, StatesGroup


class AdminSubsState(StatesGroup):
    user_id_name = State()
