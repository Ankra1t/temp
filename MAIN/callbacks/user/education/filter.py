from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

user_education_factory = CallbackData('type', 'page', 'num_les', prefix='user_education')


class UserEducationCallbackFilter(AdvancedCustomFilter):
    key = 'user_education'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
