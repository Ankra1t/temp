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

    return getButton(cancel_txt(lang), 'go_main')


def kb_main_cancel(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(cancel_btn(user_id))
    return keyboard


def kb_main(user_id: int, is_access=True, is_new_calc=False):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'calc': 'Новый расчёт',
            'settings': 'Настройки',
            'stats': 'Статистика',
        },
        'en': {
            'calc': 'New calculation',
            'settings': 'Settings',
            'stats': 'Stats',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_calc = getButton('⌨️ ' + texts[lang]['calc'], 'calc')
    btn_settings = getButton('⚙️ ' + texts[lang]['settings'], 'settings')
    btn_stats = getButton('📊 ' + texts[lang]['stats'], 'stats')

    buttons = []
    if is_access:
        buttons.append(btn_calc)
    if not is_new_calc:
        buttons.append(btn_settings)
    buttons.append(btn_stats)

    keyboard.add(*buttons)
    return keyboard
