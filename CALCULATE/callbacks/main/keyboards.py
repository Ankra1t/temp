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


def kb_set_calc_stats(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'deal': 'В сделке',
            'not_deal': 'Не в сделке',
        },
        'en': {
            'deal': 'In the deal',
            'not_deal': 'Not deal',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_deal = getButton('✅ ' + texts[lang]['deal'], 'deal')
    btn_not_deal = getButton('❌ ' + texts[lang]['not_deal'], 'not_deal')

    keyboard.add(btn_deal, btn_not_deal)

    return keyboard


def kb_freeze_calc():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_3 = getButton('3', '3')
    btn_6 = getButton('6', '6')
    btn_9 = getButton('9', '9')
    btn_12 = getButton('12', '12')
    btn_back = getButton('Отмена', 'cancel')

    keyboard.add(btn_3, btn_6)
    keyboard.add(btn_9, btn_12)
    keyboard.add(btn_back)

    return keyboard
