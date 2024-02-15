from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_new import db_new

from common.utils import get_lang
from CALCULATE.common.messages import market_translates

from .filter import settings_factory


def getButton(text: str, type: str, summury_type='', take_profit: list[int] = [], split: list[float] = []):
    return InlineKeyboardButton(
        text, None,
        callback_data=settings_factory.new(
            type=type,
            summury_type=summury_type,
            take_profit=take_profit,
            split=split
        ))


def kb_settings(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'base': 'Базовые значения',
            'lang': 'Выбрать язык',
            'tp_show': 'Установить расчет прибыли',
            'market': 'Выбрать рынок',
            'split': 'Разделение профита',
            'reset': 'Сбросить настройки',
            'summury_profit': 'Вывод профита',
            'back': 'Назад',
        },
        'en': {
            'base': 'Base values',
            'lang': 'Choose language',
            'tp_show': 'Set calculation of profit',
            'market': 'Choose market',
            'split': 'Profit splitting',
            'reset': 'Reset settings',
            'summury_profit': 'Summury profit',
            'back': 'Back'
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_base = getButton(texts[lang]["base"], 'go_change_base')
    btn_lang = getButton(texts[lang]["lang"], 'choose_lang')
    btn_back = getButton(texts[lang]["back"], 'go_main')
    btn_tp_show = getButton(texts[lang]["tp_show"], 'tp_show')
    btn_market = getButton(texts[lang]["market"], 'market')

    btn_split = getButton(texts[lang]["split"], 'split')
    btn_take_profit = getButton(
        texts[lang]["summury_profit"], 'summury_profit')

    btn_uses = getButton(texts[lang]["reset"], 'reset')

    keyboard.add(btn_base, btn_market)
    keyboard.add(btn_tp_show, btn_lang)
    keyboard.add(btn_split)
    keyboard.add(btn_take_profit)
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


def kb_change_tp_ratio(user_id: int, tp_ratio: list[int]):
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
    for el in [3, 4, 5]:
        action = 'off' if el in tp_ratio else 'on'
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


def kb_summury_profit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'change': 'Изменить',
            'back': 'Назад',
        },
        'en': {
            'change': 'Change',
            'back': 'Back',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_change = getButton(texts[lang]['change'], 'change_summury_profit')
    btn_back = getButton(texts[lang]['back'], 'go_settings')

    keyboard.add(btn_change, btn_back)
    return keyboard


def kb_summury_profit_type(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'default': 'Простой',
            'splitting': 'Разделение',
            'back': 'Назад',
        },
        'en': {
            'default': 'Default',
            'splitting': 'Splitting',
            'back': 'Back',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_default = getButton(
        texts[lang]['default'], 'change_summury_profit', 'default')
    btn_splitting = getButton(
        texts[lang]['splitting'], 'change_summury_profit', 'splitting')

    btn_back = getButton(texts[lang]['back'], 'summury_profit')

    keyboard.add(btn_default, btn_splitting)
    keyboard.add(btn_back)
    return keyboard


def kb_summury_profit_cancel(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'cancel': 'Отмена',
        },
        'en': {
            'cancel': 'Сancel',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_cancel = getButton(texts[lang]['cancel'], 'change_summury_profit', '')

    keyboard.add(btn_cancel)
    return keyboard


def kb_take_profit(user_id: int, current_tp: list[int]):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'save': 'Сохранить',
            'cancel': 'Отмена',
            'back': 'Назад',
        },
        'en': {
            'save': 'Save',
            'cancel': 'Cancel',
            'back': 'Back',
        }
    }

    tp_max = 10

    row_width = 4
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []

    if len(current_tp) != 5:
        for el in range(2, tp_max + 1):
            if el not in current_tp:
                btn = getButton(
                    f'x{el}', f'change_summury_profit',
                    'default', [*current_tp, el]
                )
                buttons.append(btn)
            if len(buttons) == row_width or (el == tp_max and len(buttons) != 0):
                keyboard.add(*buttons)
                buttons = []

    btn_save = getButton(texts[lang]['save'], 'tp_save', '', current_tp)
    btn_cancel = getButton(texts[lang]['cancel'], 'change_summury_profit')
    btn_back = getButton(
        texts[lang]['back'],
        'change_summury_profit', 'default', current_tp[:-1]
    )

    if len(current_tp) != 0:
        keyboard.add(btn_back, btn_cancel, btn_save)
    else:
        keyboard.add(btn_cancel)

    return keyboard


def kb_splitting(user_id: int, current_tp: list[int], current_split: list[float], percent_entering=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'last': 'Вывод оставшихся',
            'save': 'Сохранить',
            'cancel': 'Отмена',
            'back': 'Назад',
        },
        'en': {
            'last': 'Set for remaining',
            'save': 'Save',
            'cancel': 'Cancel',
            'back': 'Back',
        }
    }

    tp_max = 10

    percents_sum = sum(current_split)
    if abs(percents_sum - 100) < 0.1:
        percents_sum = 100

    row_width = 4
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []

    if not percent_entering and (len(current_tp) != 5 or percents_sum != 100):
        for el in range(2, tp_max + 1):
            if el not in current_tp:
                btn = getButton(
                    f'x{el}', f'change_summury_profit',
                    'splitting', [*current_tp, el], current_split
                )
                buttons.append(btn)
            if len(buttons) == row_width or (el == tp_max and len(buttons) != 0):
                keyboard.add(*buttons)
                buttons = []

    if percents_sum == 100:
        btn_save = getButton(
            texts[lang]['save'],
            'splitting_save', '',
            current_tp, current_split
        )
    else:
        btn_save = getButton(
            texts[lang]['last'],
            'splitting_last', '',
            current_tp, current_split
        )
    btn_cancel = getButton(texts[lang]['cancel'], 'change_summury_profit')
    btn_back = getButton(
        texts[lang]['back'],
        'change_summury_profit', 'splitting',
        current_tp[:-1], current_split[:-1]
    )

    if percent_entering:
        keyboard.add(btn_back, btn_cancel)
    elif len(current_tp) != 0:
        keyboard.add(btn_back, btn_cancel, btn_save)
    else:
        keyboard.add(btn_cancel)

    return keyboard


def kb_split_settings(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    is_splitting = db_new.get_user_is_splitting(user_db_id)

    texts = {
        'ru': {
            'on': 'Вкл',
            'off': 'Выкл',
            'set': 'Выставить значения',
            'back': 'Назад',
        },
        'en': {
            'on': 'On',
            'off': 'Off',
            'set': 'Set values',
            'back': 'Back',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    if is_splitting:
        btn_on_off = getButton(texts[lang]['off'], 'split_off')
    else:
        btn_on_off = getButton(texts[lang]['on'], 'split_on')

    btn_set_value = getButton(texts[lang]['set'], 'split_set_value')
    btn_back = getButton(texts[lang]['back'], 'go_settings')

    keyboard.add(btn_on_off, btn_set_value)
    keyboard.add(btn_back)

    return keyboard


def kb_split_ok(user_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)

    btn = getButton('Ок' if lang == 'ru' else 'Ok', 'split')

    keyboard.add(btn)
    return keyboard
