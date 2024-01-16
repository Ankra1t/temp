from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.utils import get_lang

from .filter import main_factory


def cancel_btn(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': 'Отмена',
        'en': 'Cancel'
    }

    return InlineKeyboardButton(
        texts[lang], callback_data=main_factory.new(type='cancel'))


def kb_cancel(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(cancel_btn(user_id))
    return keyboard


def kb_main(user_id: int, is_access=True):
    def getButton(text: str, type: str):
        return InlineKeyboardButton(
            text, None,
            callback_data=main_factory.new(type=type))

    lang = get_lang(user_id)
    texts = {
        'ru': {
            'forex': 'Форекс',
            'crypto': 'Криптовалюта',
            'paper': 'Акции',
            'future': 'Фьючерсы',
            'settings': 'Настройки',
        },
        'en': {
            'forex': 'Forex',
            'crypto': 'Cryptocurrency',
            'paper': 'Actions',
            'future': 'Futures',
            'settings': 'Settings',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(texts[lang]['forex'], 'forex')
    btn2 = getButton(texts[lang]['crypto'], 'crypto')
    btn3 = getButton(texts[lang]['paper'], 'paper')
    btn4 = getButton(texts[lang]['future'], 'future')
    btn5 = getButton(texts[lang]['settings'], 'settings')

    if is_access:
        keyboard.add(btn1, btn2)
        keyboard.add(btn3, btn4)

    keyboard.add(btn5)
    return keyboard


def kb_forex_val():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text='USD', callback_data="USD")
    btn2 = InlineKeyboardButton(text='RUB', callback_data="RUB")

    keyboard.add(btn1, btn2)
    keyboard.add(cancel_btn(0))
    return keyboard
