from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


admin_main_factory = CallbackData('type', prefix='admin_main')


class AdminMainCallbackFilter(AdvancedCustomFilter):
    key = 'admin_main'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
