from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


channel_post_factory = CallbackData('type', 'stat_id', 'is_calc', 'page', prefix='channel_post')


class ChannelPostCallbackFilter(AdvancedCustomFilter):
    key = 'channel_post'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
