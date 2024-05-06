from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


main_factory = CallbackData('type', 'stat_id', 'is_saved', prefix='main')


class MainCallbackFilter(AdvancedCustomFilter):
    key = 'main'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
