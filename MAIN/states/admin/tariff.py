from telebot.handler_backends import State, StatesGroup


class AdminTariffState(StatesGroup):
    name = State()
    duration = State()
    price = State()
    image = State()
    description = State()

    discount_percent = State()
    discount_fin_date = State()
