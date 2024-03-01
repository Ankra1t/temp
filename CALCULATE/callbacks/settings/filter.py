from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


settings_factory = CallbackData(
    'type', 'summury_type', 'take_profit', 'add_count', 'trading_style',
    prefix='settings'
)


class SettingsCallbackFilter(AdvancedCustomFilter):
    key = 'settings'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
