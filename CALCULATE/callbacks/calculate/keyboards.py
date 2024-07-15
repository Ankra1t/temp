from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.data import liteDb
from common.keyboard import back_txt, cancel_txt
from common.utils import get_lang
from db import db

from .filter import calculate_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        calculate_factory.new(type=type)
    )


def get_settings_from_calc_button():
    return getButton('⚙️', 'settings_from_calc')


def kb_pair(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=3)

    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY']

    buttons = []
    for el in pairs:
        buttons.append(getButton(el, f'pair+{el}'))

    btn_settings = get_settings_from_calc_button()
    btn_cancel = getButton(cancel_txt(lang), 'go_main')

    keyboard.add(*buttons)
    keyboard.add(btn_settings, btn_cancel)

    return keyboard


def kb_tool(user_id: int, prev_tools: list[str]):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []
    for el in prev_tools:
        if el == '':
            continue

        buttons.append(getButton(el.replace('/USDT', ''), f'tool++{el}'))
        if len(buttons) == 3:
            break

    btn_settings = get_settings_from_calc_button()
    btn_cancel = getButton(cancel_txt(lang), 'go_main')

    keyboard.add(*buttons)
    keyboard.add(btn_settings, btn_cancel)
    return keyboard


def kb_price(user_id: int, is_risk_update=False, open_price: float | None = None):
    lang = get_lang(user_id)
    is_user_risk_update = liteDb.getRiskUpdate(user_id)

    texts = {
        'ru': {
            'risk': 'риска',
        },
        'en': {
            'risk': 'of risk'
        },
        'uz': {
            'risk': 'xavf'
        },
        'tr': {
            'risk': 'risk'
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=3)

    if open_price is not None and open_price != 1.:
        btn_value = getButton(str(open_price), f'open_price+{open_price}')
        keyboard.add(btn_value)

    if is_risk_update and is_user_risk_update:
        btn_risk_50 = getButton(f'1/2 {texts[lang]["risk"]}', 'risk0.5')
        btn_risk_33 = getButton(f'1/3 {texts[lang]["risk"]}', 'risk0.33')
        keyboard.add(btn_risk_50, btn_risk_33)

    btn_settings = get_settings_from_calc_button()
    btn_cancel = getButton(cancel_txt(lang), 'go_main')
    btn_back = getButton(back_txt(lang), 'calc_back')

    keyboard.add(btn_back, btn_settings, btn_cancel)
    return keyboard


def kb_calc_cancel(user_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton(back_txt(lang), 'calc_back'),
        get_settings_from_calc_button(),
        getButton(cancel_txt(lang), 'go_main')
    )
    return keyboard


def kb_calc_atr(user_id: int, avg_atr: float | None = None):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Быстро рассчитать ATR',
        'en': 'Quickly calculate ATR',
        'uz': 'Tez hisoblang ATR',
        'tr': 'Hızla hesaplayın ATR',
    }

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton(f'⚡️ {texts[lang]}', 'calc_atr')
    )

    user_db_id = db.get_user_id_by_tg_id(user_id)
    isAdmin = db.get_worker_role(user_db_id)

    if isAdmin and avg_atr is not None:
        keyboard.add(
            getButton(f'Средний = {round(avg_atr, 2)}', f'calc_atr+')
        )

    keyboard.add(
        getButton(back_txt(lang), 'calc_back'),
        get_settings_from_calc_button(),
        getButton(cancel_txt(lang), 'go_main')
    )
    return keyboard


def kb_calc_direct(user_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton('Long', 'direct+long'),
        getButton('Short', 'direct+short'),
        getButton(cancel_txt(lang), 'calc_back'),
    )
    return keyboard
