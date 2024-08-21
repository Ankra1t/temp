from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import back_txt
from common.utils import get_lang
from models import MANUAL_TYPE, LANGUAGES_TYPE

from .filter import manual_factory


def getButton(
    text: str,
    type: str,
):
    return InlineKeyboardButton(
        text, None,
        callback_data=manual_factory.new(
            type=type,
            page=0
        ))


def kb_manuals(user_id: int, num_page: int, max_page: int):
    def getButton(text: str, type: str):
        return InlineKeyboardButton(
            text, None,
            manual_factory.new(type=type, page=num_page)
        )

    lang = get_lang(user_id)
    texts = {
        'ru': {
            'prev': 'Назад',
            'next': 'Вперед',
            'start': 'В начало',
            'end': 'В конец'
        },
        'en': {
            'prev': 'Back',
            'next': 'Next',
            'start': 'To start',
            'end': 'To end'
        },
        'uz': {
            'prev': 'Orqaga',
            'next': 'Oldinga',
            'start': 'Boshiga',
            'end': 'Oxirida'
        },
        'tr': {
            'prev': 'Geri',
            'next': 'İleri',
            'start': 'Başa',
            'end': 'Sonuna'
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_prev = getButton(texts[lang]["prev"], 'prev')
    btn_next = getButton(texts[lang]["next"], 'next')
    btn_start = getButton(texts[lang]["start"], 'start')
    btn_end = getButton(texts[lang]["end"], 'end')
    counter = getButton(f'{num_page}/{max_page}', 'counter')

    if num_page == 1:
        keyboard.add(btn_end, counter, btn_next)
    elif num_page == max_page:
        keyboard.add(btn_prev, counter, btn_start)
    else:
        keyboard.add(btn_prev, counter, btn_next)

    return keyboard


def kb_manual(user_id: int):
    row_width = 2
    lang = get_lang(user_id)
    lang = 'ru' if lang == 'ru' else 'en'

    keyboard = InlineKeyboardMarkup(row_width=row_width)

    texts: dict[LANGUAGES_TYPE, dict[MANUAL_TYPE, str]] = {
        'ru': {
            'calc': 'Калькулятор',
            'settings': 'Функционал',
            'exchange': 'Биржа',
            'trading_type': 'Тип торговли',
            'trading_style': 'Стиль торговли',
        },
        'en': {
            'calc': 'Calculator',
            'settings': 'Settings',
            'exchange': 'Exchange',
            'trading_type': 'Trading type',
            'trading_style': 'Trading style',
        },
    }

    list_types: list[MANUAL_TYPE] = [
        'calc', 'settings',
        'exchange', 'trading_type',
        'trading_style',
    ]

    buttons = []
    for el in list_types:
        buttons.append(
            getButton(texts[lang][el], f'manual+{el}')
        )

    news_link = 'profmarkets' if lang == 'ru' else 'promarketsen'
    btn_news = InlineKeyboardButton(
        'Новости' if lang == 'ru' else 'News', f'https://t.me/{news_link}'
    )
    buttons.append(btn_news)

    buttons.append(
        getButton(back_txt(lang), 'main')
    )

    keyboard.add(*buttons)

    return keyboard
