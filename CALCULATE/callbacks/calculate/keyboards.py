from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt
from common.utils import get_lang

from .filter import calculate_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        calculate_factory.new(type=type)
    )


def kb_pair(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=3)

    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY']

    buttons = []
    for el in pairs:
        buttons.append(getButton(el, f'pair+{el}'))

    btn_cancel = getButton(cancel_txt(lang), 'go_main')

    keyboard.add(*buttons)
    keyboard.add(btn_cancel)

    return keyboard


def kb_change_token(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=3)

    tokens = ['USDT', 'BTC', 'ЕТН']

    buttons = []
    for el in tokens:
        buttons.append(getButton(el, f'token+{el}'))

    btn_cancel = getButton(cancel_txt(lang), 'go_main')

    keyboard.add(*buttons)
    keyboard.add(btn_cancel)

    return keyboard


def kb_tool(user_id: int, prev_tools: list[str]):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'off': 'Пропустить',
        },
        'en': {
            'off': 'Skip',
        }
    }

    buttons = []
    for i, el in enumerate(prev_tools):
        if el == '':
            continue

        buttons.append(getButton(el, f'tool++{el}'))
        if len(buttons) == 2:
            break

    btn_cancel = getButton(cancel_txt(lang), 'go_main')
    btn_off = getButton(f'⭕️ {texts[lang]["off"]}', 'tool++**off**')

    keyboard.add(*buttons)
    keyboard.add(btn_off, btn_cancel)
    return keyboard
