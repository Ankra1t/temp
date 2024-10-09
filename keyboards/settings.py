from typing import Literal
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import back_txt, cancel_txt, reset_txt
from messages.common import transl_market, transl_tr_style, transl_tr_type
from models import LANGUAGES_TYPE, MARKETS_TYPE, STYLES, CallbackQuery
from db import db

from keyboards.stats import getButton as getStatsButton
from keyboards.calculate import get_settings_from_calc_button, calculate_factory
from services import subscribe


settings_factory = CallbackData(
    'type', 'sum_type', 'tp', 'count', 'style',
    prefix='settings'
)


class SettingsCallbackFilter(AdvancedCustomFilter):
    key = 'settings'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


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
            count=add_count if add_count is not None else '',
            style=trading_style or '',
        ))


def kb_settings(lang: LANGUAGES_TYPE, user_db_id: int):
    texts = {
        'ru': {
            'lang': 'Язык',
            'market': 'Рынок',
            'style': 'Стиль торговли',
            'trading_type': 'Тип торговли',
            'reset': 'Сброс',
            'deposit': 'Настроить торговлю',
            'summury_profit': 'Деление профита',
            'dop': 'Дополнительно',

            'exchange': 'Биржа',
            'stop': 'Вид риска',
            'active': 'Активация',
        },
        'en': {
            'lang': 'Language',
            'market': 'Market',
            'style': 'Trading style',
            'trading_type': 'Trading type',
            'reset': 'Reset',
            'deposit': 'Configure trading',
            'summury_profit': 'Profit division',
            'dop': 'Extra',

            'exchange': 'Exchange',
            'stop': 'Type of risk',
            'active': 'Activation',
        },
        'uz': {
            'lang': 'Tillar',
            'market': 'Bozor',
            'style': 'Savdo uslubi',
            'trading_type': 'Savdo turi',
            'reset': 'Qayta o\'rnatish',
            'deposit': 'Savdolarni sozlash',
            'summury_profit': 'Foyda taqsimoti',
            'dop': 'Bundan tashqari',

            'exchange': 'Almashish',
            'stop': 'Xavf turi',
            'active': 'Faollashtirish',
        },
        'tr': {
            'lang': 'Dil',
            'market': 'Pazar',
            'style': 'Ticaret tarzı',
            'trading_type': 'Ticaret türü',
            'reset': 'Sıfırla',
            'deposit': 'Ticareti yapılandırın',
            'summury_profit': 'Kâr bölümü',
            'dop': 'Ek',

            'exchange': 'Borsa',
            'stop': 'Risk türü',
            'active': 'Aktivasyon',
        },
    }

    isAdmin = db.get_worker_role(user_db_id)
    isActiveCalcSub = subscribe.check(user_db_id, 'active_calc')

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_lang = getButton('🌐 ' + texts[lang]["lang"], 'choose_lang')
    btn_market = getButton('🏬 ' + texts[lang]["market"], 'market')
    btn_style = getButton('⚖️ ' + texts[lang]["style"], 'trading_style')
    btn_trading_type = getButton(
        '🔧 ' + texts[lang]["trading_type"], 'trading_type')
    btn_deposit_update = getButton(
        '📐 ' + texts[lang]["deposit"], 'deposit_update'
    )

    btn_reset = getButton('🛑 ' + texts[lang]["reset"], 'reset')
    btn_exchange = getButton('📈 ' + texts[lang]['exchange'], 'exchange')
    btn_dop = getButton(texts[lang]['dop'], 'dop')
    btn_stop = getButton(texts[lang]['stop'], 'stop_settings')

    btn_active = getButton(texts[lang]['active'], 'active')

    btn_back = getButton(back_txt(lang), 'go_main')

    keyboard.add(btn_deposit_update)
    keyboard.add(
        btn_market, btn_exchange,
        btn_trading_type, btn_style,
        btn_stop, btn_lang,
    )

    buttons = []
    if isActiveCalcSub or isAdmin:
        buttons.append(btn_active)
    buttons.append(btn_dop)

    keyboard.add(*buttons)
    buttons = []

    keyboard.add(btn_reset, btn_back,)

    return keyboard


def kb_change_base(lang: LANGUAGES_TYPE):
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
        },
        'uz': {
            'risk': 'Xavf foizi',
            'day_risk': 'Kuniga xavf',
            'round_count': 'Yaxlitlash',
        },
        'tr': {
            'risk': 'Risk yüzdesi',
            'day_risk': 'Günlük risk',
            'round_count': 'Yuvarlama',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_risk = getButton(texts[lang]['risk'], 'set_risk_percent')
    btn_day_risk = getButton(texts[lang]['day_risk'], 'set_day_risk')
    btn_round_count = getButton(texts[lang]['round_count'], 'set_round_count')

    btn_back = getButton(back_txt(lang), 'go_settings')

    keyboard.add(btn_risk, btn_day_risk, btn_round_count, btn_back)
    return keyboard


def kb_deposit_cancel(lang: LANGUAGES_TYPE):
    btn_cancal = getButton(cancel_txt(lang), 'deposit_update')

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(btn_cancal)
    return keyboard


def kb_change_deposit(lang: LANGUAGES_TYPE, is_updating_deposit: bool, market: MARKETS_TYPE):
    texts = {
        'ru': {
            'change': 'Изменить депозит',
            'currency': 'Изменить валюту',
            'update_on': 'Вкл. обновление',
            'update_off': 'Выкл. обновление',
            'summury_profit': 'Деление профита',
        },
        'en': {
            'change': 'Change deposit',
            'currency': 'Change currency',
            'update_on': 'Update on',
            'update_off': 'Update off',
            'summury_profit': 'Profit division',
        },
        'uz': {
            'change': 'Depozitni o\'zgartirish',
            'currency': 'Valyutani almashtirish',
            'update_on': 'Yangilashni yoqing',
            'update_off': 'Yangilash o\'chirilgan',
            'summury_profit': 'Foyda taqsimoti',
        },
        'tr': {
            'change': 'Depozitoyu değiştir',
            'currency': 'Para birimini değiştir',
            'update_on': 'Güncellemeyi aç',
            'update_off': 'Güncellemeyi kapat',
            'summury_profit': 'Kâr bölümü',
        },
    }

    base = {
        'ru': {
            'risk': 'Процент риска',
            'day_risk': 'Риск на день',
            'round_count': 'Округление',
        },
        'en': {
            'risk': 'Risk percent',
            'day_risk': 'Daily risk',
            'round_count': 'Rounding',
        },
        'uz': {
            'risk': 'Xavf foizi',
            'day_risk': 'Kuniga xavf',
            'round_count': 'Yaxlitlash',
        },
        'tr': {
            'risk': 'Risk yüzdesi',
            'day_risk': 'Günlük risk',
            'round_count': 'Yuvarlama',
        },
    }

    btn_risk = getButton(base[lang]['risk'], 'set_risk_percent')
    btn_day_risk = getButton(base[lang]['day_risk'], 'set_day_risk')
    btn_round_count = getButton(base[lang]['round_count'], 'set_round_count')

    btn_summury_profit = getButton(
        '📲 ' + texts[lang]["summury_profit"], 'summury_profit'
    )

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

    # if market == 'crypto':
    #     keyboard.add(btn_back)
    # else:
    #     keyboard.add(btn_currency, btn_back)
    keyboard.add(
        btn_currency, btn_risk,
        btn_day_risk, btn_round_count,
        btn_summury_profit,
        btn_back
    )

    return keyboard


def kb_base_cancel(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(getButton(cancel_txt(lang), 'deposit_update'))
    return keyboard


def kb_change_currency(lang: LANGUAGES_TYPE, type: Literal['calc', 'welcome', ''] = ''):
    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    keyboard.add(
        getButton('USDT', f'set_currency_{type}+{"USDT"}'),
        getButton('USDC', f'set_currency_{type}+{"USDC"}')
    )

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


def kb_change_market(lang: LANGUAGES_TYPE, action: str = '', current: MARKETS_TYPE | None = None):
    row_width = 2
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons: list[InlineKeyboardButton] = []

    markets_list: tuple[MARKETS_TYPE, ...] = (
        'crypto', 'forex', 'RF', 'USA'
    )  # 'paper', 'future',
    for i, el in enumerate(markets_list):
        cur_show = '✅ ' if current == el else ''

        btn = getButton(
            cur_show + transl_market(el, lang),
            f'market_{el}{""if action == "" else f"_{action}"}'
        )
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(markets_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    if action != 'first':
        keyboard.add(getButton(cancel_txt(lang), 'go_settings'))

    return keyboard


def kb_round_count(lang: LANGUAGES_TYPE, current=-1):
    buttons = []
    for el in range(6):
        is_current = ''
        if el == current:
            is_current = '✅ '

        buttons.append(getButton(f'{is_current}{el}',
                       f'set_round_count', add_count=el))

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    keyboard.add(getButton(back_txt(lang), 'deposit_update'))
    return keyboard


def kb_choose_lang(lang: LANGUAGES_TYPE, is_first=False):
    texts = {
        'ru': {
            'ru': 'Русский',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
        'en': {
            'ru': 'Russian',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
        'uz': {
            'ru': 'Russian',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
        'tr': {
            'ru': 'Russian',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
    }

    first = 'first' if is_first else ''

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'🇷🇺 {texts[lang]["ru"]}', f'{first}_choose_lang_ru')
    btn2 = getButton(f'🇺🇸 {texts[lang]["en"]}', f'{first}_choose_lang_en')
    btn3 = getButton(f'🇺🇿 {texts[lang]["uz"]}', f'{first}_choose_lang_uz')
    btn4 = getButton(f'🇹🇷 {texts[lang]["tr"]}', f'{first}_choose_lang_tr')

    keyboard.add(btn1, btn2, btn3, btn4)
    if not is_first:
        keyboard.add(getButton(cancel_txt(lang), 'go_settings'))

    return keyboard


def kb_settings_confirm(lang: LANGUAGES_TYPE, action: str):
    texts = {
        'ru': {
            'yes': 'Да',
            'no': 'Нет',
        },
        'en': {
            'yes': 'Yes',
            'no': 'No',
        },
        'uz': {
            'yes': 'Ha',
            'no': 'Yo\'q',
        },
        'tr': {
            'yes': 'Evet',
            'no': 'HAYIR',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'✅ {texts[lang]["yes"]}', action + '_confirm_yes')
    btn2 = getButton(f'❌ {texts[lang]["no"]}', action + '_confirm_no')

    keyboard.add(btn1, btn2)
    return keyboard


def kb_summary_profit(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'change': 'Изменить',
        },
        'en': {
            'change': 'Change',
        },
        'uz': {
            'change': 'O\'zgartirish',
        },
        'tr': {
            'change': 'Değiştir',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_change = getButton(
        f"✏️ {texts[lang]['change']}", 'change_summury_profit'
    )
    btn_back = getButton(back_txt(lang), 'deposit_update')

    keyboard.add(btn_change, btn_back)
    return keyboard


def kb_summury_profit_type(lang: LANGUAGES_TYPE):
    """
        Выбор типа вывода профита
    """
    texts = {
        'ru': {
            'default': 'Простой',
            'splitting': 'Разделение',
        },
        'en': {
            'default': 'Simple',
            'splitting': 'Splitting',
        },
        'uz': {
            'default': 'Oddiy',
            'splitting': 'Ajratish',
        },
        'tr': {
            'default': 'Basit',
            'splitting': 'Ayrılma',
        },
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


def kb_take_profit(lang: LANGUAGES_TYPE, current_tp: list[int], stat_id: int | None = None):
    """
        Выбор значения коэфицента для тейк-профита
    """
    texts = {
        'ru': {
            'save': 'Сохранить',
        },
        'en': {
            'save': 'Save',
        },
        'uz': {
            'save': 'Saqlash',
        },
        'tr': {
            'save': 'Kaydet',
        },
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

            if stat_id is None:
                btn = getButton(
                    f'{added}x{el}', f'change_summury_profit',
                    'default', el
                )
            else:
                btn = getStatsButton(
                    f'{added}x{el}', f'tp_rate+{el}', stat_id=stat_id
                )

            buttons.append(btn)
            if len(buttons) == row_width or (el == tp_max and len(buttons) != 0):
                keyboard.add(*buttons)
                buttons = []

    if stat_id is None:
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
    else:
        keyboard.add(
            getStatsButton(
                back_txt(lang), 'ch_c+', stat_id
            )
        )

    return keyboard


def kb_splitting(lang: LANGUAGES_TYPE, current_tp: list[int], current_split: list[float], added_count=0):
    """
        Выбор значения коэфицента для тейк-профита, для выставления процентов
    """
    added_count = max(added_count, 1)

    texts = {
        'ru': {
            'last': 'Остаток',
            'save': 'Сохранить',
        },
        'en': {
            'last': 'Remains',
            'save': 'Save',
        },
        'uz': {
            'last': 'Qolgan',
            'save': 'Saqlash',
        },
        'tr': {
            'last': 'Kalan',
            'save': 'Kaydet',
        },
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


def kb_splitting_last(lang: LANGUAGES_TYPE):
    """
        Вывод кнопок выбора числа, на которое разделиться остаток
    """
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


def kb_trading_style(lang: LANGUAGES_TYPE, type: Literal['calc', 'welcome', 'ch_calc', 'ch_calc+stc', ''] = ''):
    def getThisButton(text: str, style: str):
        return getButton(
            text, f'ss_{type}',
            trading_style=style
        )

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    texts = {
        'ru': {
            'off_settings': 'Выключить',
            'off': 'Пропустить',
        },
        'en': {
            'off_settings': 'Off',
            'off': 'Skip',
        },
        'uz': {
            'off_settings': 'Yoqish; ishga tushirish',
            'off': 'Oʻtkazib yuborish',
        },
        'tr': {
            'off_settings': 'Kapat',
            'off': 'Atla',
        },
    }

    buttons = []
    for key in STYLES.keys():
        buttons.append(getThisButton(
            transl_tr_style(key, lang) or '', STYLES[key])
        )
        if len(buttons) == row_width:
            keyboard.add(*buttons)
            buttons = []

    if len(buttons) != 0:
        keyboard.add(*buttons)

    off_text = f'⭕️ {texts[lang]["off"]}' if type == 'calc' else f'⭕️ {texts[lang]["off_settings"]}'
    btn_off = getThisButton(off_text, '**off**')

    if type == 'calc':
        btn_back = InlineKeyboardButton(
            back_txt(lang), None, calculate_factory.new('calc_back')
        )
        btn_settings = get_settings_from_calc_button()
        btn_cancel = getButton(
            cancel_txt(lang),
            'go_main'
        )
        keyboard.add(btn_off)
        keyboard.add(btn_back, btn_settings, btn_cancel)
    elif type == 'ch_calc' or type == 'ch_calc+stc':
        btn_cancel = getThisButton(
            cancel_txt(lang),
            '**cancel**'
        )
        keyboard.add(btn_off, btn_cancel)
    else:
        btn_cancel = getButton(cancel_txt(lang), 'go_settings')
        keyboard.add(btn_off, btn_cancel)

    return keyboard


def kb_trading_type(lang: LANGUAGES_TYPE):
    btn_margin = getButton(
        transl_tr_type('margin', lang).capitalize(),
        'trading_type', trading_style='margin'
    )
    btn_spot = getButton(
        transl_tr_type('spot', lang).capitalize(),
        'trading_type', trading_style='spot'
    )
    # btn_from_dep = getButton(
    #     trading_type_translates[lang]['from_deposit'].capitalize(),
    #     'trading_type', trading_style='from_deposit'
    # )
    btn_back = getButton(back_txt(lang), 'go_settings')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_margin, btn_spot, btn_back)
    return keyboard


def kb_first_calc_info(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Настроить свой калькулятор',
        'en': 'Set up your calculator',
        'uz': 'Kalkulyatoringizni sozlang',
        'tr': 'Hesap makinenizi özelleştirin',
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton(f'⚙️ {texts[lang]}', 'set_first_settings'),
    )
    return keyboard


def kb_exchange(lang: LANGUAGES_TYPE, is_exchange: bool = False):
    texts = {
        'ru': {
            'set_exchange': 'Установить биржу',
            'change_exchange': 'Изменить биржу',
            'change_fee': 'Изменить комиссию',
            'off': 'Отключение',
        },
        'en': {
            'set_exchange': 'Set exchange',
            'change_exchange': 'Change exchange',
            'change_fee': 'Change the fee',
            'off': 'Off',
        },
        'uz': {
            'set_exchange': 'Almashinuvni o\'rnating',
            'change_exchange': 'O\'zgartirish almashinuvi',
            'change_fee': 'Komissiyani o\'zgartirish',
            'off': 'Yoqish; ishga tushirish',
        },
        'tr': {
            'set_exchange': 'Borsayı ayarla',
            'change_exchange': 'borsayı değiştir',
            'change_fee': 'Komisyonu değiştir',
            'off': 'Kapat',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=3)

    if is_exchange:
        keyboard.add(
            getButton(texts[lang]['change_exchange'], 'set_exchange'),
            getButton(texts[lang]['change_fee'], 'set_fee'),
        )
        keyboard.add(
            # getButton(f'⭕️ {texts[lang]["off"]}', 'off_exchange'),
            getButton(back_txt(lang), 'go_settings')
        )
    else:
        keyboard.add(
            getButton(texts[lang]['set_exchange'], 'set_exchange'),
        )
        keyboard.add(getButton(back_txt(lang), 'go_settings'))

    return keyboard


def kb_change_style_settings(lang: LANGUAGES_TYPE, is_style_change: bool):
    texts = {
        'ru': {
            'set_style': 'Изменить стиль',
            'on': 'Включить изменение',
            'off': 'Выключить изменение',
        },
        'en': {
            'set_style': 'Change style',
            'on': 'Turn on the change',
            'off': 'Turn off the change',
        },
        'uz': {
            'set_style': "O'zgartirish uslubi",
            'on': "O'zgarishni yoqing",
            'off': "O'zgarishlarni o'chiring",
        },
        'tr': {
            'set_style': 'Değişim Stili',
            'on': 'Değişikliği aç',
            'off': 'Değişikliği kapat',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton(texts[lang]['set_style'], 'ss_'),
        getButton(
            texts[lang]['off' if is_style_change else 'on'],
            'switch_style_change'
        ),
        getButton(back_txt(lang), 'go_settings')
    )
    return keyboard


def kb_maker_or_taker(lang: LANGUAGES_TYPE, name: str, maker_fee: float, taker_fee: float):
    texts = {
        'ru': {
            'maker': 'Мейкер',
            'taker': 'Тейкер',
        },
        'en': {
            'maker': 'Maker',
            'taker': 'Taker',
        },
        'uz': {
            'maker': 'Maker',
            'taker': 'Taker',
        },
        'tr': {
            'maker': 'Yapıcı',
            'taker': 'Alıcı',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        getButton(texts[lang]['maker'], f'set_ex_fee++{name}++{maker_fee}'),
        getButton(texts[lang]['taker'], f'set_ex_fee++{name}++{taker_fee}'),
        getButton(cancel_txt(lang), 'exchange')
    )

    return keyboard


def kb_enter_exchange(lang: LANGUAGES_TYPE, values: list[str] = [], is_first=False):
    if len(values) == 0:
        values = ['Bybit', 'Binance', 'OKX', 'KuCoin']

    buttons = []
    for el in values:
        buttons.append(getButton(el, f'set_exchange++{el}'))
    buttons.append(
        getButton(back_txt(lang), 'go_settings' if is_first else 'exchange')
    )

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard


def kb_choose_exchange_level(lang: LANGUAGES_TYPE, exchange: str, values: list[str]):
    buttons = []
    for el in values:
        buttons.append(getButton(el, f'set_ex_lvl++{exchange}++{el}'))
    buttons.append(getButton(back_txt(lang), 'exchange'))

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def kb_change_fee(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(back_txt(lang), 'go_settings'))
    return keyboard


def kb_dop_settings(lang: LANGUAGES_TYPE, output: Literal['text', 'photo'], risk_upd: bool):
    texts = {
        'ru': {
            'calc_output': 'Вывод расчета: ' + ('текстом 📝' if output == 'photo' else 'картинкой 🖼'),

            'on': '✅ Вкл.',
            'off': '⭕️ Выкл.',
            'is_risk_update': 'изменение риска',
        },
        'en': {
            'calc_output': 'Calc output: ' + ('in text 📝' if output == 'photo' else 'in image 🖼'),
            'dop': 'Extra',

            'on': '✅ On',
            'off': '⭕️ Off',
            'is_risk_update': 'risk update',
        },
        'uz': {
            'calc_output': 'Hisoblash xulosasi: ' + ('matnni bilan 📝' if output == 'photo' else 'rasm bilan  🖼'),
            'dop': 'Bundan tashqari',

            'on': '✅ Yoqish',
            'off': '⭕️ O\'chirish',
            'is_risk_update': 'xavfni yangilash',
        },
        'tr': {
            'calc_output': 'Hesaplamanın çıktısı: ' + ('metinle 📝' if output == 'photo' else 'resimle 🖼'),
            'dop': 'Ek',

            'on': '✅ Dahil etmek',
            'off': '⭕️ Kapamak',
            'is_risk_update': 'risk güncellemesi',
        },
    }

    btn_output = getButton(texts[lang]['calc_output'], 'calc_output')
    btn_risk_update = getButton(
        f'{texts[lang]["off" if risk_upd else "on"]} {texts[lang]["is_risk_update"]}',
        'set_risk_update'
    )

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(btn_output)
    keyboard.add(btn_risk_update)
    keyboard.add(getButton(back_txt(lang), 'go_settings'))
    return keyboard


def kb_choose_stop_type(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'simple': 'Простой',
            'atr': 'ATR',
            'atr_percent': '% от ATR',
            'from_deposit': "Торговля от депозита",
        },
        'en': {
            'simple': 'Simple',
            'atr': 'ATR',
            'atr_percent': '% of ATR',
            'from_deposit': "Trading from a deposit",
        },
        'uz': {
            'simple': 'Oddiy',
            'atr': 'ATR',
            'atr_percent': '% ATR',
            'from_deposit': "Omonatdan savdo",
        },
        'tr': {
            'simple': 'Basit',
            'atr': 'ATR',
            'atr_percent': 'ATR %',
            'from_deposit': "Depozitodan ticaret",
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton(texts[lang]['simple'], 'set_stop+default'),
        getButton(texts[lang]['atr'], 'set_stop+atr'),
        getButton(texts[lang]['atr_percent'], 'set_stop+atr_percent'),
    )
    keyboard.add(getButton(texts[lang]['from_deposit'], 'change_fr_dp'))

    buttons = []
    buttons.append(getButton(back_txt(lang), 'go_settings'))
    keyboard.add(*buttons)
    return keyboard


def kb_stop_type_cancel(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(cancel_txt(lang), 'stop_settings'))
    return keyboard


def kb_atr_settings(lang: LANGUAGES_TYPE, atr_settings: tuple[bool, str]):
    texts = {
        'ru': {
            'change': 'Изменить бары',
            'auto': 'Авто расчёт' + (' ✅' if atr_settings[0] else ''),
            'self': 'Ручной расчёт' + (' ✅' if not atr_settings[0] else '')
        },
        'en': {
            'change': 'Change bars',
            'auto': 'Auto calculation' + (' ✅' if atr_settings[0] else ''),
            'self': 'Manual calculation' + (' ✅' if not atr_settings[0] else '')
        },
        'uz': {
            'change': 'Barlarni almashtirish',
            'auto': 'Avtomatik hisoblash' + (' ✅' if atr_settings[0] else ''),
            'self': 'Qo\'lda hisoblash' + (' ✅' if not atr_settings[0] else '')
        },
        'tr': {
            'change': 'Çubukları Değiştir',
            'auto': 'Otomatik hesaplama' + (' ✅' if atr_settings[0] else ''),
            'self': 'Manuel hesaplama' + (' ✅' if not atr_settings[0] else '')
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton(
            texts[lang]['auto'],
            'atr_auto'
        ),
        getButton(
            texts[lang]['self'],
            'atr_self'
        ),
    )
    keyboard.add(getButton(texts[lang]['change'], 'atr_bars'))
    keyboard.add(getButton(back_txt(lang), 'stop_settings'))
    return keyboard


def kb_atr_bars(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=4)
    keyboard.add(
        getButton('15m', 'set_atr_bars+15m'),
        getButton('1h', 'set_atr_bars+1h'),
        getButton('4h', 'set_atr_bars+4h'),
        getButton('1d', 'set_atr_bars+1d'),
        getButton(cancel_txt(lang), 'atr_settings')
    )
    return keyboard


def kb_atr_bars_count(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton('1', 'set_atr_count+1'),
        getButton('5', 'set_atr_count+5'),
        getButton('10', 'set_atr_count+10'),
        getButton(cancel_txt(lang), 'atr_settings')
    )
    return keyboard


def kb_first_dep(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'Настроить',
        'en': 'Settings',
        'uz': 'Sozlamoq',
        'tr': 'Ayarlamak',
    }

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton('⚙️ ' + text[lang], 'first_dep')
    )
    return keyboard


def kb_active_settings(lang: LANGUAGES_TYPE, autoStop: bool):
    texts = {
        'ru': {
            'cancelAt': 'Время отмены',
            'tr_stop': 'Ск. стоп',
            'auto_stop': 'Авто стоп',
            'auto_take': 'Авто тейк',
            'cancel': 'Отменить сделку',
            'profit': 'Закрыть сделку',
        },
        'en': {
            'cancelAt': 'Cancel at',
            'tr_stop': 'Trailing stop',
            'auto_stop': 'Auto stop',
            'auto_take': 'Auto take',
            'cancel': 'Cancel the deal',
            'profit': 'Close the deal ',
        },
        'uz': {
            'cancelAt': 'Bekor qilish vaqti',
            'tr_stop': 'Slip stop',
            'auto_stop': 'Avtomatik to\'xtatish',
            'auto_take': 'Avtoulov',
            'cancel': 'Bitimni bekor qiling',
            'profit': 'Bitimni yoping',
        },
        'tr': {
            'cancelAt': 'Iptal etmek',
            'tr_stop': 'Kayan durdurma',
            'auto_stop': 'Otomatik durdurma',
            'auto_take': 'Otomatik alım',
            'cancel': 'Anlaşmayı iptal et',
            'profit': 'Anlaşmayı kapat ',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        getButton(
            texts[lang]['cancelAt'], 'cancel_at'
        ),
        getButton(
            texts[lang]['tr_stop'], 'tr_stop'
        ),
        getButton(
            ('✅' if not autoStop else '❌') +
            ' ' + texts[lang]['auto_stop'],
            'auto_stop'
        ),
        getButton(
            texts[lang]['auto_take'],
            'auto_take'
        ),
        getButton(
            back_txt(lang), 'go_settings',
        ),
    )

    return keyboard


def kb_settings_cancel_at(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton('1h', 'cancel_at+1h'),
        getButton('4h', 'cancel_at+4h'),
        getButton('1d', 'cancel_at+1d'),
    )
    keyboard.add(
        getButton(reset_txt(lang), 'cancel_at+0'),
        getButton(back_txt(lang), 'active')
    )
    return keyboard


def kb_settings_auto_take(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=5)

    buttons = []
    for i in range(1, 11):
        buttons.append(
            getButton(f'{i}', f'auto_take+{i}')
        )

    keyboard.add(*buttons)
    keyboard.add(
        getButton(back_txt(lang), 'active')
    )
    return keyboard


def kb_settings_tr_stop(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=4)

    buttons = []
    for i in range(1, 5):
        buttons.append(
            getButton(f'{i}', f'tr_stop+{i}')
        )

    keyboard.add(*buttons)
    keyboard.add(
        getButton(reset_txt(lang), 'tr_stop+0'),
        getButton(back_txt(lang), 'active')
    )
    return keyboard
