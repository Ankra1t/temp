from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.utils import get_lang
from CALCULATE.common.messages import market_translates

from .filter import settings_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        callback_data=settings_factory.new(type=type))


def kb_settings(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'base': 'Базовые значения',
            'lang': 'Выбрать язык',
            'tp_show': 'Установить расчет прибыли',
            'market': 'Выбрать рынок',
            'uses': 'Сброс использования',
            'back': 'Назад',
        },
        'en': {
            'base': 'Base values',
            'lang': 'Choose language',
            'tp_show': 'Set calculation of profit',
            'market': 'Choose market',
            'uses': 'Сброс использования',
            'back': 'Back'
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_base = getButton(texts[lang]["base"], 'go_change_base')
    btn_lang = getButton(texts[lang]["lang"], 'choose_lang')
    btn_back = getButton(texts[lang]["back"], 'go_main')
    btn_tp_show = getButton(texts[lang]["tp_show"], 'tp_show')
    btn_market = getButton(texts[lang]["market"], 'market')

    btn_uses = getButton(texts[lang]["uses"], 'uses')

    keyboard.add(btn_base, btn_market)
    keyboard.add(btn_tp_show, btn_lang)
    keyboard.add(btn_uses, btn_back)
    return keyboard


def kb_change_base(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'dep': 'Депозит',
            'risk': 'Процент риска',
            'currency': 'Валюта',
            'back': 'Назад'
        },
        'en': {
            'dep': 'Deposit',
            'risk': 'Risk percent',
            'currency': 'Currency',
            'back': 'Back'
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_dep = getButton(texts[lang]['dep'], 'set_deposit')
    btn_risk = getButton(texts[lang]['risk'], 'set_risk_percent')
    btn_currency = getButton(texts[lang]['currency'], 'set_currency')
    btn_back = getButton(texts[lang]['back'], 'go_settings')

    keyboard.add(btn_dep, btn_risk)
    keyboard.add(btn_currency)
    keyboard.add(btn_back)
    return keyboard


def kb_change_currency(user_id: int):
    lang = get_lang(user_id)

    back = {
        'ru': 'Назад',
        'en': 'Back',
    }

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    currency_list = ['USD', 'USDT', 'EUR', 'RUB', 'CNY', 'JPY']
    buttons: list[InlineKeyboardButton] = []
    for i, el in enumerate(currency_list):
        btn = getButton(el, f'set_currency+{el}')
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(currency_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    btn_back = getButton(back[lang], 'go_settings')
    keyboard.add(btn_back)
    return keyboard


def kb_change_tp_show(user_id: int, tp_show: str):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'on': 'Вкл',
            'off': 'Выкл',
            'back': 'Назад'
        },
        'en': {
            'on': 'On',
            'off': 'Off',
            'back': 'Назад'
        }
    }

    buttons = []
    for el in ['3', '4', '5']:
        action = 'off' if el in tp_show else 'on'
        btn = getButton(f'{texts[lang][action]} x{el}',
                        f'tp_show_{el}_{action}')
        buttons.append(btn)

    back = getButton(texts[lang]['back'], 'go_settings')

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    keyboard.add(back)
    return keyboard


def kb_change_market(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'back': 'Назад'
        },
        'en': {
            'back': 'Back'
        }
    }

    row_width = 2
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons: list[InlineKeyboardButton] = []

    markets_list = ('crypto', 'forex')  # 'paper', 'future',
    for i, el in enumerate(markets_list):
        btn = getButton(market_translates[lang][el], f'market_{el}')
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(markets_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    btn_back = getButton(texts[lang]['back'], 'go_settings')
    keyboard.add(btn_back)

    return keyboard


def kb_base_cancel(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': 'Назад',
        'en': 'Back'
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn = getButton(texts[lang], 'go_change_base')

    keyboard.add(btn)
    return keyboard


def kb_choose_lang(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'ru': 'Русский',
            'en': 'Английский',
            'back': 'Назад'
        },
        'en': {
            'ru': 'Russian',
            'en': 'English',
            'back': 'Back'
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'🇷🇺 {texts[lang]["ru"]}', 'choose_lang_ru')
    btn2 = getButton(f'🇺🇸 {texts[lang]["en"]}', 'choose_lang_en')
    btn_back = getButton(texts[lang]["back"], 'go_settings')

    keyboard.add(btn1, btn2)
    keyboard.add(btn_back)
    return keyboard


def kb_settings_confirm(user_id: int, action: str):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'yes': 'Да',
            'no': 'Нет',
        },
        'en': {
            'yes': 'Yes',
            'no': 'No',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'{texts[lang]["yes"]}', action + '_confirm_yes')
    btn2 = getButton(f'{texts[lang]["no"]}', action + '_confirm_no')

    keyboard.add(btn1, btn2)
    return keyboard
