from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


manual_factory = CallbackData('type', 'page', prefix='manual')


class ManualCallbackFilter(AdvancedCustomFilter):
    key = 'manual'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)