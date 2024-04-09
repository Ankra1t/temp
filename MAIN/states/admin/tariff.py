from telebot.handler_backends import State, StatesGroup


class AdminTariffState(StatesGroup):
    name = State()
    price = State()
    duration = State()
    image = State()
    image_en = State()
    description = State()

    discount_percent = State()
    discount_datetime = State()
