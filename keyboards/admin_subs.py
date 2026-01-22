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


def kb_admin_subs_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    back = getButton(back_txt(), 'back')
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


def kb_admin_subs_list(page: int, count_pages: int):
    keyboard = InlineKeyboardMarkup(row_width=3)

    if count_pages > 1:
        counter = getButton(f'{page}/{count_pages}', 'counter')

        if page == 1:
            btn_left = getButton('<<', f'list+{count_pages}')
        else:
            btn_left = getButton('<', f'list+{page-1}')

        if page == count_pages:
            btn_right = getButton('>>', 'list+1')
        else:
            btn_right = getButton('>', f'list+{page+1}')

        keyboard.add(btn_left, counter, btn_right)

    back = getButton(back_txt(), 'back')
    keyboard.add(back)
    return keyboard
