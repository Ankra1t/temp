from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from models import CallbackQuery

from common.keyboard import back_txt
from common.utils import get_calculator_btn_link


admin_params_factory = CallbackData('type', prefix='admin_params')


class AdminParamsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_params'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, admin_params_factory.new(type=type))


def kb_params():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_calc = getButton('⌨️ Калькулятор', 'calculator')

    back = getButton(back_txt(), 'go_main')

    keyboard.add(btn_calc)
    keyboard.add(back)
    return keyboard


def kb_calculator():
    keyboard = InlineKeyboardMarkup(row_width=2)

    back = getButton(back_txt(), 'go_params')
    btn_link = get_calculator_btn_link('ru')

    keyboard.add(btn_link)
    keyboard.add(back)
    return keyboard
