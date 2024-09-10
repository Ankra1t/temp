from telebot.asyncio_handler_backends import State, StatesGroup


class StatsState(StatesGroup):
    loss = State()
    sum = State()

    freeze = State()

    add_image_text = State()

    send_add_text = State()
    send_add_photo = State()

    cancel_at = State()

class ChannelCalcState(StatesGroup):
    loss = State()