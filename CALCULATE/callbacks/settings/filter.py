from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


settings_factory = CallbackData(
    'type', 'sum_type', 'tp', 'count', 'style',
    prefix='settings'
)


class SettingsCallbackFilter(AdvancedCustomFilter):
    key = 'settings'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
