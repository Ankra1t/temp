from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.utils import get_lang
from CALCULATE.callbacks.main.filter import main_factory


def kb_support(user_id: int, link: str):
    link = link.replace('@', '')
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'operator': 'Перейти к оператору',
            'back': 'Главную',
        },
        'en': {
            'operator': 'Go to the operator',
            'back': 'Main',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_link = InlineKeyboardButton(
        texts[lang]['operator'], f'https://t.me/{link}'
    )
    btn_back = InlineKeyboardButton(
        texts[lang]['back'], callback_data=main_factory.new(type='cancel')
    )

    keyboard.add(btn_link, btn_back)
    return keyboard
