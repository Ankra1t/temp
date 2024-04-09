from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


calculate_factory = CallbackData('type', prefix='calculate')


class CalculateCallbackFilter(AdvancedCustomFilter):
    key = 'calculate'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
