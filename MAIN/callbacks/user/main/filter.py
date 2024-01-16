from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

user_main_factory = CallbackData('type', prefix='user_main')


class UserMainCallbackFilter(AdvancedCustomFilter):
    key = 'user_main'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
