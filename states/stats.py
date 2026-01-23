from telebot.states import State, StatesGroup


class StatsState(StatesGroup):
    loss = State()
    sum = State()

    freeze = State()

    add_image_text = State()

    send_add_text = State()
    send_add_photo = State()

    cancel_at = State()
    new_stop = State()
    trailing_stop = State()
    close_price = State()

    take_price = State()


class ChannelCalcState(StatesGroup):
    loss = State()
