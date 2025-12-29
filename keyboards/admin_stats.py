from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from common.keyboard import back_txt

from models import CallbackQuery


admin_statistics_factory = CallbackData('type', 'filter', prefix='admin_stats')


class AdminStatisticsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_stats'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str, filter=''):
    return InlineKeyboardButton(text, None, admin_statistics_factory.new(
        type=type, filter=filter
    ))


def kb_statistics_back():
    keyboard = InlineKeyboardMarkup(row_width=2)

    back = getButton(back_txt(), 'go_payment')

    keyboard.add(back)
    return keyboard
