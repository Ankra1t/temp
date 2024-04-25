from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt
from common.utils import get_lang

from ..stats.keyboards import kb_calc_result
from .filter import main_factory


def getButton(text: str, type: str, is_new_calc=False, stat_id=-1):
    return InlineKeyboardButton(
        text, None,
        main_factory.new(
            type=type,
            stat_id=str(stat_id),
            is_new_calc=str(is_new_calc)
        )
    )


def cancel_btn(user_id: int):
    lang = get_lang(user_id)

    return getButton(cancel_txt(lang), 'go_main')


def kb_main_cancel(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_settings = getButton('⚙️', 'settings')

    keyboard.add(btn_settings, cancel_btn(user_id))
    return keyboard


def kb_main(user_id: int, is_access=True, is_new_calc=False, stat_id=-1):
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

    btn_calc = getButton(
        '⌨️ ' + texts[lang]
        ['calc'], 'calc', is_new_calc, stat_id
    )
    btn_settings = getButton(
        '⚙️ ' + texts[lang]['settings'], 'settings', is_new_calc, stat_id)
    btn_stats = getButton('📊 ' + texts[lang]['stats'], 'stats')

    buttons = []
    if is_access:
        buttons.append(btn_calc)
    if not is_new_calc:
        buttons.append(btn_stats)
    buttons.append(btn_settings)

    if stat_id != -1:
        kb = kb_calc_result(user_id, stat_id)
        buttons_rows = kb.keyboard

        for row in buttons_rows:
            keyboard.add(*row, row_width=kb.row_width)

    keyboard.add(*buttons)
    return keyboard
