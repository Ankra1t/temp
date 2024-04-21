from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


stats_factory = CallbackData('type', 'stat_id', 'stats_market', prefix='stats')


class StatsCallbackFilter(AdvancedCustomFilter):
    key = 'stats'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
