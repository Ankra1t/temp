from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

admin_params_factory = CallbackData('type', prefix='admin_params')


class AdminParamsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_params'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
