from telebot.handler_backends import State, StatesGroup


class AdminTariffState(StatesGroup):
    name = State()
    duration = State()
    price = State()
    image = State()
    description = State()

    discount_percent = State()
    discount_fin_date = State()

    choose_edit_field = State()
    edit_field_name = State()
    edit_field_duration = State()
    edit_field_description = State()
    edit_field_price = State()
    edit_field_image = State()

