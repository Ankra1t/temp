from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt
from common.utils import get_lang

from db_new import db_new

from .filter import main_factory


def getButton(text: str, type: str, stat_id = 0):
    return InlineKeyboardButton(
        text, None,
        main_factory.new(type=type, stat_id=stat_id)
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
    buttons.append(btn_settings)

    keyboard.add(*buttons)
    keyboard.add(btn_stats)
    return keyboard


def kb_forex_val(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('USD', callback_data="USD")
    btn2 = InlineKeyboardButton('RUB', callback_data="RUB")

    keyboard.add(btn1, btn2)
    keyboard.add(cancel_btn(user_id))
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


def kb_freeze_calc():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_3 = getButton('3 ч', '3')
    btn_6 = getButton('6 ч', '6')
    btn_9 = getButton('9 ч', '9')
    btn_12 = getButton('12 ч', '12')
    btn_back = getButton('Отмена', 'cancel')

    keyboard.add(btn_3, btn_6)
    keyboard.add(btn_9, btn_12)
    keyboard.add(btn_back)

    return keyboard


def kb_deal_result(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    tp = db_new.get_calculator_tp_ratio(user_db_id)

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
