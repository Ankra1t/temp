from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt
from common.utils import get_lang

from .filter import main_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        main_factory.new(type=type)
    )


def cancel_btn(user_id: int):
    lang = get_lang(user_id)

    return getButton(cancel_txt(lang), 'cancel')


def kb_cancel(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(cancel_btn(user_id))
    return keyboard


def kb_main(user_id: int, is_access=True):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'calc': 'Новый расчёт',
            'settings': 'Настройки',
        },
        'en': {
            'calc': 'New calculation',
            'settings': 'Settings',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_calc = getButton('⌨️ ' + texts[lang]['calc'], 'calc')
    btn_settings = getButton('⚙️ ' + texts[lang]['settings'], 'settings')

    buttons = []
    if is_access:
        buttons.append(btn_calc)
    buttons.append(btn_settings)

    keyboard.add(*buttons)
    return keyboard


def kb_forex_val(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('USD', callback_data="USD")
    btn2 = InlineKeyboardButton('RUB', callback_data="RUB")

    keyboard.add(btn1, btn2)
    keyboard.add(cancel_btn(user_id))
    return keyboard
