from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.utils import get_lang


def kb_support(user_id: int, link: str):
    link = link.replace('@', '')
    lang = get_lang(user_id)

    texts = {
        'ru': 'Перейти к оператору',
        'en': 'Go to the operator'
    }

    keyboard = InlineKeyboardMarkup(row_width=1)

    btn_link = InlineKeyboardButton(
        texts[lang], f'https://t.me/{link}'
    )

    keyboard.add(btn_link)
    return keyboard
