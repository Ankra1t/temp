from typing import Literal
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from CALCULATE.common.messages import market_translates
from common.keyboard import back_txt, cancel_txt
from common.utils import get_lang

from db import db
from models import MARKETS_TYPE

from .filter import stats_factory


def getButton(text: str, type: str, stat_id=0, stats_market: MARKETS_TYPE = 'crypto'):
    return InlineKeyboardButton(
        text, None,
        stats_factory.new(
            type=type,
            stat_id=stat_id,
            stats_market=stats_market,
        )
    )


def kb_stats(user_id: int, type: Literal['main', 'market'] = 'main', prev_market: MARKETS_TYPE | None = None):
    lang = get_lang(user_id)

    row_width = 2
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []
    markets_list: tuple[MARKETS_TYPE, ...] = (
        'crypto', 'forex', 'RF', 'USA'
    )  # 'paper', 'future',
    for i, el in enumerate(markets_list):
        btn = getButton(
            market_translates[lang][el],
            'stats_market' if el != prev_market else '',
            -1, el
        )
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(markets_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    if type == 'main':
        btn_back = getButton(back_txt(lang), 'go_main')
    else:
        btn_back = getButton(back_txt(lang), 'go_stats')

    keyboard.add(btn_back)
    return keyboard


def kb_calc_result(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'save': 'Сохранить в статистику',
            'del': 'Удалить',
            'change': 'Изменить',
        },
        'en': {
            'save': 'Save to stats',
            'del': 'Delete',
            'change': 'Change',
        }
    }

    btn_save = getButton(f'✅ {texts[lang]["save"]}', 'profit+', stat_id)
    btn_delete = getButton(f'❌ {texts[lang]["del"]}', 'delete_calc', stat_id)
    btn_change = getButton(
        f'✏️ {texts[lang]["change"]}', 'change_calc', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_delete, btn_change, btn_save)

    return keyboard


def kb_freeze_calc(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    hours = {
        'ru': 'ч',
        'en': 'h'
    }

    btn_3 = getButton(f'3 {hours[lang]}', 'time+3')
    btn_6 = getButton(f'6 {hours[lang]}', 'time+6')
    btn_9 = getButton(f'9 {hours[lang]}', 'time+9')
    btn_12 = getButton(f'12 {hours[lang]}', 'time+12')
    btn_back = getButton(cancel_txt(lang), 'profit+cancel')

    keyboard.add(btn_3, btn_6)
    keyboard.add(btn_9, btn_12)
    keyboard.add(btn_back)

    return keyboard


def kb_deal_result(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'minus': 'Стоп-лосс',
            'sum': 'Иная сумма',
        },
        'en': {
            'minus': 'Stop-loss',
            'sum': 'Other profit',
        }
    }

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
            buttons = []

    btn_low = getButton(f'{texts[lang]["minus"]}', 'profit+-', stat_id)
    btn_sum = getButton(f'{texts[lang]["sum"]}', 'sum', stat_id)
    btn_back = getButton(cancel_txt(lang), 'profit+cancel', stat_id)

    keyboard.add(btn_sum, btn_low, btn_back)

    return keyboard


def kb_deal_profit_minus(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_cancel = getButton(back_txt(lang), 'profit+cancel', stat_id)
    btn_x1 = getButton('x1', 'profit+loss1', stat_id)
    btn_x1_5 = getButton('x1.5', 'profit+loss1.5', stat_id)
    btn_x2 = getButton('x2', 'profit+loss2', stat_id)

    keyboard.add(btn_x1, btn_x1_5, btn_x2, btn_cancel)
    return keyboard


def kb_deal_profit_cancel(user_id: int, stat_id: int):
    lang = get_lang(user_id)
    btn_cancel = getButton(cancel_txt(lang), 'profit+cancel', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_cancel)
    return keyboard


def kb_calculate_delete(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'yes': 'Да',
            'no': 'Нет',
        },
        'en': {
            'yes': 'Yes',
            'no': 'No',
        },
    }

    btn_yes = getButton(f'✅ {texts[lang]["yes"]}', 'delete_calc_yes', stat_id)
    btn_no = getButton(f'❌ {texts[lang]["no"]}', 'delete_calc_no', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_no, btn_yes)
    return keyboard


def kb_calculate_change(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'open_price': 'Цену входа',
            'stop_loss': 'Стоп-лосс',
            'tool': 'Инструмент',
        },
        'en': {
            'open_price': 'Open price',
            'stop_loss': 'Stop-loss',
            'tool': 'Tool',
        },
    }

    btn_op = getButton(texts[lang]["open_price"], 'change_calc+open_price', stat_id)
    btn_sl = getButton(texts[lang]["stop_loss"], 'change_calc+stop_loss', stat_id)
    btn_tool = getButton(texts[lang]["tool"], 'change_calc+tool', stat_id)
    btn_back = getButton(back_txt(lang), 'change_calc+back', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_op, btn_sl)
    keyboard.add(btn_tool, btn_back)
    return keyboard
