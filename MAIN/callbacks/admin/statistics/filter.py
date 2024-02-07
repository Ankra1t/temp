from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

admin_statistics_factory = CallbackData('type', 'filter', prefix='admin_stats')


class AdminStatisticsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_stats'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
