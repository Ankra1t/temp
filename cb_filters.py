from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot import types

admin_default_factory = CallbackData('type', prefix='admin_default')

adm_action = CallbackData('action', 'id', prefix='adm_act')


class AdminDefaultCallbackFilter(AdvancedCustomFilter):
    key = 'admin_default'  # нужен при фильтрации колбека

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


class AdminActionsCallbackFilter(AdvancedCustomFilter):
    key = 'action'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(call)

