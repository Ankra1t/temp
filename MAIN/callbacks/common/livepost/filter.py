from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


livepost_factory = CallbackData('type', 'value', prefix='livepost')


class LivepostCallbackFilter(AdvancedCustomFilter):
    key = 'livepost'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
