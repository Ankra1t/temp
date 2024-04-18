from telebot.handler_backends import State, StatesGroup


class AdminParamsState(StatesGroup):
    text = State()

    forex_pair = State()
    forex_price = State()
    forex_help_pair = State()

    count_trial_days = State()
