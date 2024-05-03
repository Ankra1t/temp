from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

user_tariff_factory = CallbackData('type', 'tariff_id', 'page', 'tariff_type', prefix='user_tariff')


class UserTariffCallbackFilter(AdvancedCustomFilter):
    key = 'user_tariff'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
