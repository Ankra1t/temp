from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from models import CallbackQuery

from common.keyboard import back_txt


admin_subs_factory = CallbackData('type', prefix='admin_subs')


class AdminSubsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_subs'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, admin_subs_factory.new(type=type))


def kb_admin_subs():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_set = getButton('Выдать подписку', 'set')
    back = getButton(back_txt(), 'go_main')

    keyboard.add(btn_set)
    keyboard.add(back)
    return keyboard

def kb_admin_subs_back():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_set = getButton('Активация сделок', 'set+active_calc')
    back = getButton(back_txt(), 'back')

    keyboard.add(btn_set)
    keyboard.add(back)
    return keyboard


def kb_admin_subs_choose_type():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_set = getButton('Активация сделок', 'set+active_calc')
    back = getButton(back_txt(), 'back')

    keyboard.add(btn_set)
    keyboard.add(back)
    return keyboard


def kb_admin_subs_choose_user():
    keyboard = InlineKeyboardMarkup(row_width=2)

    back = getButton(back_txt(), 'set')

    keyboard.add(back)
    return keyboard
