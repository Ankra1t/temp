from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import back_txt, cancel_txt
from common.utils import get_lang

from db import db

from .filter import stats_factory


def getButton(text: str, type: str, stat_id=0):
    return InlineKeyboardButton(
        text, None,
        stats_factory.new(type=type, stat_id=stat_id)
    )


def kb_stats(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            '': '',
        },
        'en': {
            '': '',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_deal = getButton(back_txt(lang), 'go_main')

    keyboard.add(btn_deal)
    return keyboard


def kb_set_calc_stats(user_id: int, stat_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'save': 'Сохранить расчет',
        },
        'en': {
            'save': 'Save calculation',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_deal = getButton('✅ ' + texts[lang]['save'], 'profit+', stat_id)

    keyboard.add(btn_deal)
    return keyboard


def kb_freeze_calc(user_id: int):
    lang = get_lang(0)
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_3 = getButton('3 ч', 'time+3')
    btn_6 = getButton('6 ч', 'time+6')
    btn_9 = getButton('9 ч', 'time+9')
    btn_12 = getButton('12 ч', 'time+12')
    btn_back = getButton(cancel_txt(lang), 'profit+cancel')

    keyboard.add(btn_3, btn_6)
    keyboard.add(btn_9, btn_12)
    keyboard.add(btn_back)

    return keyboard


def kb_deal_result(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    calc_info = db.get_calculation(stat_id)
    tp: list[int] = getattr(calc_info, 'tp_ratio', [])

    buttons = []
    for i, el in enumerate(tp):
        btn = getButton(f'x{el}', f'profit+{el}', stat_id)
        buttons.append(btn)
        if len(buttons) == row_width or (i == len(tp) - 1 and len(buttons) != 0):
            keyboard.add(*buttons)

    btn_low = getButton('🔻 Минус', 'profit+-', stat_id)
    btn_back = getButton(cancel_txt(lang), 'profit+cancel', stat_id)

    keyboard.add(btn_low, btn_back)

    return keyboard


def kb_deal_profit_minus(user_id: int, stat_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'loss': 'Ровно',
        },
        'en': {
            'loss': 'Ровно',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_cancel = getButton(cancel_txt(lang), 'profit+cancel', stat_id)
    btn_loss = getButton(texts[lang]['loss'], 'profit+loss', stat_id)

    keyboard.add(btn_loss, btn_cancel)
    return keyboard
