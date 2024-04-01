from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery


admin_tariffs_factory = CallbackData(
    'type', 'page', 'id', prefix='admin_tariffs'
)


class AdminTariffsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_tariffs'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)
