from telebot.asyncio_handler_backends import State, StatesGroup


class AdminPostsState(StatesGroup):
    live = State()
    name = State()
    ticker = State()

    signal_values = State()
    content = State()
    datetime = State()
    confirm_add = State()

    post_delete = State()
    post_send = State()
    comfirm_send_delete = State()

    edit_text = State()
