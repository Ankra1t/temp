from telebot.asyncio_handler_backends import State, StatesGroup


class AdminParamsState(StatesGroup):
    text = State()

    count_trial_days = State()


class AdminMainState(StatesGroup):
    turnover = State()
