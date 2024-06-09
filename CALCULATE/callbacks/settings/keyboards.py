from typing import Literal
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import back_txt, cancel_txt
from common.utils import get_lang
from CALCULATE.common.messages import market_translates
from models import MARKETS_TYPE

from .filter import settings_factory
from ..calculate.keyboards import get_settings_from_calc_button
from ..calculate.filter import calculate_factory


def getButton(
    text: str,
    type: str,
    summury_type='',
    take_profit: int | None = None,
    add_count: int | None = None,
    trading_style: str | None = None
):
    return InlineKeyboardButton(
        text, None,
        callback_data=settings_factory.new(
            type=type,
            sum_type=summury_type,
            tp=take_profit or '',
            count=add_count or '',
            style=trading_style or '',
        ))


def kb_settings(user_id: int, cur_calc_output: Literal['text', 'photo'], is_risk_update=False):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'base': 'Базовые значения',
            'lang': 'Язык',
            'market': 'Рынок',
            'style': 'Стиль торговли',
            'trading_type': 'Тип торговли',
            'reset': 'Сброс',
            'deposit': 'Депозит',
            'summury_profit': 'Деление профита',
            'calc_output': 'Вывод расчета: ' + ('текстом' if cur_calc_output == 'photo' else 'картинкой'),

            'on': 'Вкл.',
            'off': 'Выкл.',
            'is_risk_update': 'изменение риска',

            'exchange': 'Биржа'
        },
        'en': {
            'base': 'Base values',
            'lang': 'Language',
            'market': 'Market',
            'style': 'Trading style',
            'trading_type': 'Trading type',
            'reset': 'Reset',
            'deposit': 'Deposit',
            'summury_profit': 'Profit division',
            'calc_output': 'Calc output: ' + ('in text' if cur_calc_output == 'photo' else 'in image'),

            'on': 'On',
            'off': 'Off',
            'is_risk_update': 'risk update',

            'exchange': 'Биржа'
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_base = getButton('📊 ' + texts[lang]["base"], 'go_change_base')
    btn_lang = getButton('🌐 ' + texts[lang]["lang"], 'choose_lang')
    btn_market = getButton('🏬 ' + texts[lang]["market"], 'market')
    btn_style = getButton('⚖️ ' + texts[lang]["style"], 'trading_style')
    btn_trading_type = getButton(
        '🔧 ' + texts[lang]["trading_type"], 'trading_type')
    btn_deposit_update = getButton(
        '📐 ' + texts[lang]["deposit"], 'deposit_update')

    btn_summury_profit = getButton(
        '📲 ' + texts[lang]["summury_profit"], 'summury_profit'
    )

    btn_reset = getButton('🛑 ' + texts[lang]["reset"], 'reset')
    btn_output = getButton(texts[lang]['calc_output'], 'calc_output')
    btn_exchange = getButton(texts[lang]['exchange'], 'exchange')
    btn_back = getButton(back_txt(lang), 'go_main')

    btn_risk_update = getButton(
        f'{texts[lang]["off" if is_risk_update else "on"]} {texts[lang]["is_risk_update"]}',
        'set_risk_update'
    )

    keyboard.add(btn_market, btn_deposit_update)
    keyboard.add(btn_base, btn_summury_profit)
    keyboard.add(btn_style, btn_trading_type)
    keyboard.add(btn_lang, btn_reset)
    keyboard.add(btn_output)
    keyboard.add(btn_risk_update)
    keyboard.add(btn_exchange, btn_back)
    return keyboard


def kb_change_base(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'risk': 'Процент риска',
            'day_risk': 'Риск на день',
            'round_count': 'Округление',
        },
        'en': {
            'risk': 'Risk percent',
            'day_risk': 'Daily risk',
            'round_count': 'Rounding',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_risk = getButton(texts[lang]['risk'], 'set_risk_percent')
    btn_day_risk = getButton(texts[lang]['day_risk'], 'set_day_risk')
    btn_round_count = getButton(texts[lang]['round_count'], 'set_round_count')

    btn_back = getButton(back_txt(lang), 'go_settings')

    keyboard.add(btn_risk, btn_day_risk, btn_round_count, btn_back)
    return keyboard


def kb_deposit_cancel(user_id: int):
    lang = get_lang(user_id)

    btn_cancal = getButton(cancel_txt(lang), 'deposit_update')

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(btn_cancal)
    return keyboard


def kb_change_deposit(user_id: int, is_updating_deposit: bool, market: MARKETS_TYPE):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'change': 'Изменить депозит',
            'currency': 'Изменить валюту',
            'update_on': 'Вкл. обновление',
            'update_off': 'Выкл. обновление',
        },
        'en': {
            'change': 'Change deposit',
            'currency': 'Change currency',
            'update_on': 'Update on',
            'update_off': 'Update off',
        },
    }

    btn_change = getButton(texts[lang]['change'], 'set_deposit')
    btn_currency = getButton(texts[lang]['currency'], 'set_currency')
    btn_on = getButton(f'✅ {texts[lang]["update_on"]}', 'deposit_update_on')
    btn_off = getButton(
        f'⭕️ {texts[lang]["update_off"]}', 'deposit_update_off'
    )
    btn_back = getButton(back_txt(lang), 'go_settings')

    keyboard = InlineKeyboardMarkup(row_width=2)
    if is_updating_deposit:
        keyboard.add(btn_change, btn_off)
    else:
        keyboard.add(btn_change, btn_on)

    if market == 'crypto':
        keyboard.add(btn_back)
    else:
        keyboard.add(btn_currency, btn_back)

    return keyboard


def kb_base_cancel(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn = getButton(cancel_txt(lang), 'go_change_base')

    keyboard.add(btn)
    return keyboard


def kb_change_currency(user_id: int, type: Literal['calc', 'welcome', ''] = ''):
    lang = get_lang(user_id)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    currency_list = ['USD', 'GBP', 'EUR', 'RUB', 'CNY', 'JPY']
    buttons: list[InlineKeyboardButton] = []
    for i, el in enumerate(currency_list):
        btn = getButton(el, f'set_currency_{type}+{el}')
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(currency_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    if type == 'calc':
        btn_settings = get_settings_from_calc_button()
        btn_back = getButton(cancel_txt(lang), 'go_main')
        keyboard.add(btn_settings, btn_back)
    else:
        btn_back = getButton(cancel_txt(lang), 'go_settings')
        keyboard.add(btn_back)

    return keyboard


def kb_change_market(user_id: int):
    lang = get_lang(user_id)

    row_width = 2
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons: list[InlineKeyboardButton] = []

    markets_list: tuple[MARKETS_TYPE, ...] = (
        'crypto', 'forex', 'RF', 'USA')  # 'paper', 'future',
    for i, el in enumerate(markets_list):
        btn = getButton(market_translates[lang][el], f'market_{el}')
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(markets_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    btn_back = getButton(cancel_txt(lang), 'go_settings')
    keyboard.add(btn_back)

    return keyboard


def kb_choose_lang(user_id: int, is_first=False):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'ru': 'Русский',
            'en': 'English',
        },
        'en': {
            'ru': 'Russian',
            'en': 'English',
        }
    }

    first = 'first' if is_first else ''

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'🇷🇺 {texts[lang]["ru"]}', f'{first}_choose_lang_ru')
    btn2 = getButton(f'🇺🇸 {texts[lang]["en"]}', f'{first}_choose_lang_en')

    keyboard.add(btn1, btn2)
    if not is_first:
        keyboard.add(getButton(cancel_txt(lang), 'go_settings'))

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

    btn1 = getButton(f'✅ {texts[lang]["yes"]}', action + '_confirm_yes')
    btn2 = getButton(f'❌ {texts[lang]["no"]}', action + '_confirm_no')

    keyboard.add(btn1, btn2)
    return keyboard


def kb_summury_profit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'change': 'Изменить',
        },
        'en': {
            'change': 'Change',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_change = getButton(
        f"✏️ {texts[lang]['change']}", 'change_summury_profit'
    )
    btn_back = getButton(back_txt(lang), 'go_settings')

    keyboard.add(btn_change, btn_back)
    return keyboard


def kb_summury_profit_type(user_id: int):
    """
        Выбор типа вывода профита
    """
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'default': 'Простой',
            'splitting': 'Разделение',
        },
        'en': {
            'default': 'Simple',
            'splitting': 'Splitting',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_default = getButton(
        texts[lang]['default'], 'change_summury_profit', 'default'
    )
    btn_splitting = getButton(
        texts[lang]['splitting'], 'change_summury_profit', 'splitting'
    )

    btn_back = getButton(back_txt(lang), 'summury_profit')

    keyboard.add(btn_default, btn_splitting)
    keyboard.add(btn_back)
    return keyboard


def kb_take_profit(user_id: int, current_tp: list[int]):
    """
        Выбор значения коэфицента для тейк-профита
    """
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'save': 'Сохранить',
        },
        'en': {
            'save': 'Save',
        }
    }

    # Максимальный тейк-профит
    tp_max = 10
    # Максимальное кол-во тейк-профитов
    tp_count_max = 5

    row_width = 4
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []

    # Если кол-во тейк-профитов еще не максимальное - выводим кнопки
    if len(current_tp) != tp_count_max:
        for el in range(2, tp_max + 1):
            added = '✅ ' if el in current_tp else ''
            btn = getButton(
                f'{added}x{el}', f'change_summury_profit',
                'default', el
            )
            buttons.append(btn)
            if len(buttons) == row_width or (el == tp_max and len(buttons) != 0):
                keyboard.add(*buttons)
                buttons = []

    # Сохранение выбранного
    btn_save = getButton('✅ ' + texts[lang]['save'], 'tp_save')

    # Отмена, выход к выбору типа
    btn_cancel = getButton(
        cancel_txt(lang), 'change_summury_profit'
    )

    # Шаг назад, убираем последний тейк-профит
    btn_back = getButton(
        back_txt(lang),
        'change_summury_profit', 'default', None, -1
    )

    if len(current_tp) != 0:
        keyboard.add(btn_back, btn_cancel, btn_save)
    else:  # Если еще ничего не выбрано, выводим только кнопку отмены
        keyboard.add(btn_cancel)

    return keyboard


def kb_splitting(user_id: int, current_tp: list[int], current_split: list[float], added_count=0):
    """
        Выбор значения коэфицента для тейк-профита, для выставления процентов
    """
    added_count = max(added_count, 1)
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'last': 'Остаток',
            'save': 'Сохранить',
        },
        'en': {
            'last': 'Remains',
            'save': 'Save',
        }
    }

    # Максимальный тейк-профит
    tp_max = 10
    # Максимальное кол-во тейк-профитов
    tp_count_max = 5

    percents_sum = sum(current_split)
    if abs(percents_sum - 100) < 0.2:
        percents_sum = 100

    row_width = 4
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []

    # Если кол-во не максимульное и сумма процентов не 100
    if len(current_tp) != tp_count_max and percents_sum != 100:
        for el in range(2, tp_max + 1):
            max_tp = max([*current_tp, 0])
            if el > max_tp:
                btn = getButton(
                    f'x{el}', f'change_summury_profit',
                    'splitting', el
                )
                buttons.append(btn)
            if len(buttons) == row_width or (el == tp_max and len(buttons) != 0):
                keyboard.add(*buttons)
                buttons = []

    # Кнопка сохранения, если сумма процентов равна 100
    if percents_sum == 100:
        btn_save = getButton(
            '✅ ' + texts[lang]['save'],
            'splitting_save'
        )
    # Иначе кнопка для распределения остатка
    else:
        btn_save = getButton(
            '✏️ ' + texts[lang]['last'],
            'splitting_last'
        )

    # Отмена, выход к выбору типа
    btn_cancel = getButton(
        cancel_txt(lang), 'change_summury_profit')

    # Шаг назад, убираем последний тейк-профит и его процент
    btn_back = getButton(
        back_txt(lang),
        'change_summury_profit', 'splitting', None, -added_count
    )

    if len(current_tp) != 0:
        keyboard.add(btn_back, btn_cancel, btn_save)
    else:  # Если еще ничего не выбрано, выводим только кнопку отмены
        keyboard.add(btn_cancel)

    return keyboard


def kb_splitting_last(user_id: int):
    """
        Вывод кнопок выбора числа, на которое разделиться остаток
    """
    lang = get_lang(user_id)

    ratio_max = 4
    row_width = 4

    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []
    for el in range(1, ratio_max + 1):
        btn = getButton(
            str(el), 'change_summury_profit',
            'splitting', None, el
        )
        buttons.append(btn)

    keyboard.add(*buttons)

    btn_cancel = getButton(
        cancel_txt(lang), 'change_summury_profit'
    )
    btn_back = getButton(
        back_txt(lang),
        'change_summury_profit', 'splitting',
    )

    keyboard.add(btn_back, btn_cancel)
    return keyboard


def kb_trading_style(user_id: int, type: Literal['calc', 'welcome', 'ch_calc', ''] = ''):
    def getThisButton(text: str, style: str):
        return getButton(
            text, f'style_{type}',
            trading_style=style
        )

    lang = get_lang(user_id)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    styles = {
        'Пробой': 'пробой уровня',
        'Отбой': 'отбой от уровня',
        'Ложные': 'ложные пробои',
        'Скользящие': 'скользящие средние',
        'high/low': 'торговля на high/low',
    }

    texts = {
        'ru': {
            'off_settings': 'Выключить',
            'off': 'Пропустить',
        },
        'en': {
            'off_settings': 'Off',
            'off': 'Skip',
        }
    }

    buttons = []
    for key in styles.keys():
        buttons.append(getThisButton(key, styles[key]))
        if len(buttons) == row_width:
            keyboard.add(*buttons)
            buttons = []

    off_text = f'⭕️ {texts[lang]["off"]}' if type == 'calc' else f'⭕️ {texts[lang]["off_settings"]}'
    btn_off = getThisButton(off_text, '**off**')

    buttons.append(btn_off)
    if len(buttons) != 0:
        keyboard.add(*buttons)

    if type == 'calc':
        btn_back = InlineKeyboardButton(
            back_txt(lang), None, calculate_factory.new('calc_back')
        )
        btn_settings = get_settings_from_calc_button()
        btn_cancel = getButton(
            cancel_txt(lang),
            'go_main'
        )
        keyboard.add(btn_back, btn_settings, btn_cancel)
    elif type == 'ch_calc':
        btn_cancel = getThisButton(
            cancel_txt(lang),
            '**cancel**'
        )
        keyboard.add(btn_cancel)
    else:
        btn_cancel = getButton(cancel_txt(lang), 'go_settings')
        keyboard.add(btn_cancel)

    return keyboard


def kb_trading_type(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'margin': 'Маржинальный',
            'spot': 'Спотовый',
        },
        'en': {
            'margin': 'Margin',
            'spot': 'Spot',
        },
    }

    btn_margin = getButton(texts[lang]['margin'],
                           'trading_type', trading_style='margin')
    btn_spot = getButton(texts[lang]['spot'],
                         'trading_type', trading_style='spot')
    btn_back = getButton(back_txt(lang), 'go_settings')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_margin, btn_spot)
    keyboard.add(btn_back)
    return keyboard


def kb_first_calc_info(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Настроить свой калькулятор',
        'en': 'Set up your calculator',
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton(f'⚙️ {texts[lang]}', 'set_first_settings'),
    )
    return keyboard


def kb_exchange(user_id: int, is_exchange: bool = False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'set_exchange': 'Установить биржу',
            'change_exchange': 'Изменить биржу',
            'change_fee': 'Изменить комиссию',
        },
        'en': {
            'set_exchange': 'Set exchange',
            'change_exchange': 'Change exchange',
            'change_fee': 'Change fee',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=3)

    if is_exchange:
        keyboard.add(
            getButton(texts[lang]['change_exchange'], 'set_exchange'),
            getButton(texts[lang]['change_fee'], 'set_fee'),
        )
    else:
        keyboard.add(
            getButton(texts[lang]['set_exchange'], 'set_exchange'),
        )

    keyboard.add(getButton(back_txt(lang), 'go_settings'))
    return keyboard


def kb_maker_or_taker(user_id: int, name: str, maker_fee: float, taker_fee: float):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'maker': 'Мейкер',
            'taker': 'Тейкер',
        },
        'en': {
            'maker': 'Maker',
            'taker': 'Taker',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        getButton(texts[lang]['maker'], f'set_ex_fee++{name}++{maker_fee}'),
        getButton(texts[lang]['taker'], f'set_ex_fee++{name}++{taker_fee}'),
        getButton(cancel_txt(lang), 'exchange')
    )

    return keyboard


def kb_enter_exchange(user_id: int, values: list[str] = []):
    lang = get_lang(user_id)

    if len(values) == 0:
        values = ['Bybit', 'Binance', 'OKX', 'KuCoin']

    buttons = []
    for el in values:
        buttons.append(getButton(el, f'set_exchange++{el}'))
    buttons.append(getButton(back_txt(lang), 'exchange'))

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard


def kb_choose_exchange_level(user_id: int, exchange: str,  values: list[str]):
    lang = get_lang(user_id)

    buttons = []
    for el in values:
        buttons.append(getButton(el, f'set_ex_lvl++{exchange}++{el}'))
    buttons.append(getButton(back_txt(lang), 'exchange'))

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def kb_change_fee(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(back_txt(lang), 'go_settings'))
    return keyboard


def kb_try(user_id: int):
    lang = get_lang(user_id)

    text = 'Попробовать' if lang == 'ru' else 'Try'

    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(text, 'first_try'))
    return keyboard