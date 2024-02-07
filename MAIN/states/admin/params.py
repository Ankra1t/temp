from telebot.handler_backends import State, StatesGroup


class AdminParamsState(StatesGroup):
    text = State()

    future_name = State()
    future_step = State()
    future_price_step = State()

    forex_pair = State()
    forex_price = State()
    forex_help_pair = State()

    count_trial_days = State()
