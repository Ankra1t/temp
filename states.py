from telebot.handler_backends import State, StatesGroup  # State


class AdmLivePost(StatesGroup):
    disabled = State()
    enabled = State()


class AdmUsers(StatesGroup):
    main = State()
    wait_username = State()
    count_days = State()
