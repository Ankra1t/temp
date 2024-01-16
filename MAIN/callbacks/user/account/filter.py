from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

user_account_factory = CallbackData('type', prefix='user_account')


class UserAccountCallbackFilter(AdvancedCustomFilter):
    key = 'user_account'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
