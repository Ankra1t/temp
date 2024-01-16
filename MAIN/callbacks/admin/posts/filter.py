from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery

admin_posts_factory = CallbackData('type', prefix='admin_posts')


class AdminPostsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_posts'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
