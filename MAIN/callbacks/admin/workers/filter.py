from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


admin_workers_factory = CallbackData(
    'type', 'id', 'name', 'role', prefix='admin_workers')


class AdminWorkersCallbackFilter(AdvancedCustomFilter):
    key = 'admin_workers'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
