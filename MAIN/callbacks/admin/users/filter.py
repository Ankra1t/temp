from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


admin_users_factory = CallbackData(
    'type', 'filter', 'client_db_id', 'page', prefix='admin_users')


class AdminUsersCallbackFilter(AdvancedCustomFilter):
    key = 'admin_users'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
