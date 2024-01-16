from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.utils import get_lang

from .filter import manual_factory


def kb_manual(user_id: int, num_page: int, max_page: int):
    def getButton(text: str, type: str):
        return InlineKeyboardButton(
            text, None,
            manual_factory.new(type=type, page=num_page))

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
        }
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
