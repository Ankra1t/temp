from typing import Literal
from telebot import TeleBot
from datetime import datetime

from Classes import text_editor
from common.dt import get_str_by_datetime
from common.utils import get_decimal_count, get_lang, get_print_float
from db import LANGUAGES_TYPE, db
from data.data import liteDb
from Classes import calcService
from models import MARKETS_TYPE, TRADING_TYPE, Calculation, CalculatorStats, ForexInfo


POINT = '•'
TAB = '   '
ENTER = '\n'


market_translates: dict[LANGUAGES_TYPE, dict[MARKETS_TYPE, str]] = {
    'ru': {
        'crypto': 'Криптовалюты',
        'paper': 'Акции',
        'forex': 'Форекс',
        'RF': 'РФ',
        'USA': 'США',
    },
    'en': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    },
    'uz': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    },
    'tr': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    },
}

trading_styles_translates = {
    'пробой уровня': 'breakout',
    'отбой от уровня': 'bounce',
    'ложные пробои': 'fakeout',
    'скользящие средние': 'moving average',
    'торговля на high/low': 'high/low trading',
}

trading_type_translates: dict[LANGUAGES_TYPE, dict[TRADING_TYPE, str]] = {
    'ru': {
        'margin': 'маржинальный',
        'spot': 'спотовый',
    },
    'en': {
        'margin': 'margin',
        'spot': 'spot',
    },
    'uz': {
        'margin': 'marjasi',
        'spot': 'sple',
    },
    'tr': {
        'margin': 'marj',
        'spot': 'spot',
    },
}


def txt_current_value(lang: LANGUAGES_TYPE):
    if lang == 'ru':
        return 'Текущее значение'
    elif lang == 'uz':
        return 'Hozirgi qiymat'
    elif lang == 'tr':
        return 'Mevcut değeri'
    else:
        return 'Current value'


def get_risk_annotation(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            '1': '<i>Cо знаком %</i> - для ввода процента от депозита',
            '2': '<i>Без знаков</i> - для ввода точной суммы',
        },
        'en': {
            '1': '<i>With a sign of %</i> - for entering a percentage from a deposit',
            '2': '<i>Without signs</i> - for entering a exact amount',
        },
        'uz': {
            '1': '% belgisi bilan - omonat foizini kiritish uchun',
            '2': 'Belgilarsiz - aniq miqdorni kiritish uchun',
        },
        'tr': {
            '1': '<i>% işaretiyle</i> - yatırılan tutarın yüzdesini girmek için',
            '2': '<i>İşaretsiz</i> - tam tutarı girmek için',
        },
    }

    return f"""{texts[lang]['1']}
{texts[lang]['2']}
"""


def get_freeze_annotation(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'time': 'Введите <i>время</i> заморозки в формате <u>ЧЧ:ММ</u>',
            'datetime': 'Либо <i>дату до</i> в формате <u>ДД.ММ.ГГГГ ЧЧ:ММ</u>',
        },
        'en': {
            'time': 'Enter <i>time</i> frost in format <u>HH:MM</u>',
            'datetime': 'Or <i>date to</i> in format <u>ДД.ММ.ГГГГ ЧЧ:ММ</u>',
        },
        'uz': {
            'time': 'Muzlatish vaqtini HH:MM formatida kiriting',
            'datetime': 'Yoki DD.MM.YYYY HH:MM formatida "sanagacha"',
        },
        'tr': {
            'time': ' Donma <i>zamanını</i> <u>SS:DD</u> formatında girin',
            'datetime': 'Veya <i>tarihi</i> <u>GG.AA.YYYY SS:DD</u> formatında',
        },
    }

    return f"""✍️ {texts[lang]['time']}.
✍️ {texts[lang]['datetime']}."""


# Основные страницы
def msg_uses_count(user_id: int, count: int):
    lang = get_lang(user_id)

    text = {
        'ru': {
            'uses': 'Бесплатных расчетов',
        },
        'en': {
            'uses': 'Free calculations left',
        },
        'uz': {
            'uses': 'Bepul hisob-kitoblar',
        },
        'tr': {
            'uses': 'Kalan ücretsiz hesaplama',
        },
    }

    return f'{text[lang]["uses"]}: <b>{count}</b>'


def msg_main(user_id: int, uses_count: int, is_rus=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Меню',
            '1': 'Настройте калькулятор',
            '2': 'Получите точные расчеты',
            'uses': 'Бесплатных расчетов',
        },
        'en': {
            'name': 'Menu',
            '1': 'Choose the market',
            '2': 'Get accurate calculations',
            'uses': 'Free calculations left',
        },
        'uz': {
            'name': 'Menyu',
            '1': 'Bozorni tanlang',
            '2': 'To\'g\'ri hisob-kitoblarni oling',
            'uses': 'Bepul hisob-kitoblar qoldi',
        },
        'tr': {
            'name': 'Menü',
            '1': 'Pazarı seçin',
            '2': 'Doğru hesaplamalar alın',
            'uses': 'Ücretsiz hesaplamalar kaldı',
        },
    }

    return f"""
⚡️ <b><u>{texts[lang]["name"]}</u></b>

1. <b>{texts[lang]["1"]}</b>
2. <b>{texts[lang]["2"]}</b>

{msg_uses_count(user_id, uses_count) if not is_rus else ''}
"""


def msg_no_uses(user_id: int):
    lang = get_lang(user_id)
    text = {
        'ru': {
            '1': 'Тестовые 100 использований закончились',
            '2': 'Перейдите в бота рекомендаций для покупки доступа'
        },
        'en': {
            '1': '100 test uses are over',
            '2': 'Go to the signal bot for buying access'
        },
        'uz': {
            '1': 'Test 100 ta foydalanish tugadi',
            '2': 'Kirishni sotib olish uchun bot tavsiyalariga o\'ting'
        },
        'tr': {
            '1': '100 kullanımlık test erişim sona erdi',
            '2': 'Erişim satın almak için öneri botuna gidiniz'
        },
    }

    return f"""
❗️ {text[lang]["1"]}
{text[lang]["2"]}
"""


def msg_main_freeze(user_id: int, freeze_dt: datetime):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Меню',
        },
        'en': {
            'name': 'Menu',
        },
        'uz': {
            'name': 'Menyu',
        },
        'tr': {
            'name': 'Menü',
        },
    }

    return f"""⚡️ <b><u>{texts[lang]["name"]}</u></b>

{msg_frozen(user_id, get_str_by_datetime(freeze_dt))}
"""


def msg_settings(user_id: int, is_risk_update=False):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    calc_output = db.get_user_calc_output(user_db_id)

    u_base = db.get_calc_user_settings(user_db_id)
    if u_base is None:
        return ''

    texts = {
        'ru': {
            'name': 'Настройки',
            'dep': 'Базовый депозит',
            'risk': 'Базовый риск',
            'day_risk': 'Риск на день',
            'round_count': 'Округление до',
            'trading_style': 'Стиль торговли',
            'trading_type': 'Тип торговли',
            'updating_deposit': 'Обновление депозита',
            'tp_show': 'Деление профита',
            'market': 'Рынок',
            'round_count': 'Округление',
            'on': 'Включено',
            'off': 'Выключено',

            'output': 'Вывод расчета',
            'by_text': 'текстом',
            'by_image': 'картинкой',

            'is_risk_update': 'Изменение риска во время расчета'
        },
        'en': {
            'name': 'Settings',
            'dep': 'Default deposit',
            'risk': 'Default risk',
            'day_risk': 'Daily risk',
            'round_count': 'Rounding',
            'trading_style': 'Trading style',
            'trading_type': 'Trading type',
            'updating_deposit': 'Deposit updating',
            'tp_show': 'Profit division',
            'market': 'Market',
            'on': 'On',
            'off': 'Off',

            'output': 'Calc output',
            'by_text': 'in text',
            'by_image': 'in image',

            'is_risk_update': 'Changing of risk at the time of calculation'
        },
        'uz': {
            'name': 'Sozlamalar',
            'dep': 'Asosiy depozit',
            'risk': 'Asosiy xavf',
            'day_risk': 'Kundalik xavf',
            'round_count': 'Yaxlitlash',
            'trading_style': 'Savdo uslubi',
            'trading_type': 'Savdo turi',
            'updating_deposit': 'Depozitni yangilash',
            'tp_show': 'Foyda taqsimoti',
            'market': 'Bozor',
            'on': 'Haqida',
            'off': 'Yopiq',

            'output': 'Hisoblash chiqishi',
            'by_text': 'matnda',
            'by_image': 'rasmda',

            'is_risk_update': 'Hisoblash paytida xavfning o\'zgarishi'
        },
        'tr': {
            'name': 'Ayarlar',
            'dep': 'Temel depozito',
            'risk': 'Temel risk',
            'day_risk': 'Günlük risk',
            'round_count': 'Rounding',
            'trading_style': 'Ticaret tarzı',
            'trading_type': 'Ticaret türü',
            'updating_deposit': 'Depozito güncellemesi',
            'tp_show': 'Kâr paylaşımı',
            'market': 'Pazar',
            'on': 'Üzerinde',
            'off': 'Kapalı',

            'output': 'Hesaplama çıktısı',
            'by_text': 'metinde',
            'by_image': 'görüntüde',

            'is_risk_update': 'Hesaplama sırasında risk değişimi'
        },
    }

    currency = u_base.currency or ''

    tp_result = ''
    for el in u_base.tp_ratio:
        tp_result += f'x{el} '

    show_deposit = '-'
    if u_base.deposit is not None:
        show_deposit = get_print_float(u_base.deposit)

    show_risk = (str(get_print_float(u_base.risk[0])) +
                 ("%" if u_base.risk[1] else f" {currency}")) if (u_base.risk is not None) else "-"

    show_day_risk = (f'{get_print_float(u_base.day_risk[0])}' +
                     ('%' if u_base.day_risk[1] else f' {currency}')) if (u_base.day_risk is not None) else "-"

    updating_deposit = texts[lang]['off']
    if u_base.is_updating_deposit:
        updating_deposit = texts[lang]['on']

    return f"""
⚙️ <b><u>{texts[lang]["name"]}</u></b>

{POINT} {texts[lang]["market"]}: <b>{market_translates[lang][u_base.market]}</b>

{POINT} {texts[lang]["dep"]}: <b>{show_deposit} {currency}</b>
{POINT} {texts[lang]["risk"]}: <b>{show_risk}</b>
{POINT} {texts[lang]["updating_deposit"]}: <b>{updating_deposit}</b>

{POINT} {texts[lang]["trading_style"]}: <b>{u_base.trading_style or '-'}</b>
{POINT} {texts[lang]["trading_type"]}: <b>{trading_type_translates[lang][u_base.trading_type]}</b>
{POINT} {texts[lang]["tp_show"]}: <b>{tp_result}</b>

{POINT} {texts[lang]["day_risk"]}: <b>{show_day_risk}</b>
{POINT} {texts[lang]["round_count"]}: <b>{u_base.round_count or '-'}</b>

{POINT} {texts[lang]["output"]}: <b>{texts[lang]['by_text'] if calc_output == 'text' else texts[lang]['by_image']}</b>
{POINT} {texts[lang]["is_risk_update"]}: <b>{texts[lang]['on'] if is_risk_update else texts[lang]['off']}</b>"""


def msg_deposit(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    stop = liteDb.getUserStop(user_id)

    if stop is None:
        stop_show = '-'
    elif stop == 'default':
        stop_show = '-'
    elif stop == 'atr':
        stop_show = 'ATR'
    else:
        _, percent = stop.split('+')
        stop_show = f'{percent}% of ATR'

    is_update = False
    deposit = '-'
    currency = 'USD'
    round_count = '-'
    if u_base is not None:
        deposit = get_print_float(u_base.deposit or 0.) or deposit
        currency = u_base.currency or currency
        is_update = u_base.is_updating_deposit
        round_count = u_base.round_count if u_base.round_count is not None else round_count

    texts = {
        'ru': {
            'main': 'Настройка депозита',
            'dep': 'Текущий депозит',
            'update': 'Обновление депозита',
            'on': 'включено',
            'round_count': 'Округление',
            'stop': 'Вид риска',
            'off': 'выключено',
        },
        'en': {
            'main': 'Deposit setup',
            'dep': 'Current deposit',
            'update': 'Updating the deposit',
            'on': 'on',
            'round_count': 'Rounding',
            'stop': 'Type of risk',
            'off': 'off',
        },
        'uz': {
            'main': 'Depozit sozlamalari',
            'dep': 'Joriy depozit',
            'update': 'Omonatni yangilash',
            'on': 'yoqilgan',
            'round_count': 'Yaxlitlash',
            'stop': 'Xavf turi',
            'off': 'o\'chirilgan',
        },
        'tr': {
            'main': 'Depozito ayarları',
            'dep': 'Vadeli mevduat',
            'update': 'Depozitoyu güncellemek',
            'on': 'etkin',
            'round_count': 'Yuvarlama',
            'stop': 'Risk türü',
            'off': 'kapalı',
        },
    }

    return f"""<b><u>{texts[lang]['main']}</u></b>

{POINT} {texts[lang]['dep']}: <b>{deposit} {currency}</b>
{POINT} {texts[lang]['round_count']}: <b>{round_count}</b>
{POINT} {texts[lang]['stop']}: <b>{stop_show}</b>
{POINT} {texts[lang]['update']}: <b>{texts[lang]['on'] if is_update else texts[lang]['off']}</b>
"""


def msg_change_style_settings(user_id: int, style: str, style_update_on: bool):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Настройка стиля торговли',
            'update': 'Изменение во время расчёта',
            'on': 'включено',
            'off': 'выключено',
        },
        'en': {
            'main': 'Setting up the style of trade',
            '': 'present value',
            'update': 'Change during calculation',
            'on': 'turned on',
            'off': 'turned off',
        },
        'uz': {
            'main': 'Savdo uslubini yaratish',
            'update': "Hisoblash paytida o'zgarish",
            'on': 'kiritilgan',
            'off': "o'chirilgan",
        },
        'tr': {
            'main': 'Ticaret tarzını kurmak',
            'update': 'Hesaplama Sırasında Değiş',
            'on': 'dahil',
            'off': 'kapalı',
        },
    }

    return f"""<b><u>{texts[lang]['main']}</u></b>

{POINT} {txt_current_value(lang)}: <b>{style}</b>
{POINT} {texts[lang]['update']}: <b>{texts[lang]['on'] if style_update_on else texts[lang]['off']}</b>
"""


def msg_settings_change_base(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Изменение значений',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Change base',
        },
        'uz': {
            'name': 'Sozlamalar',
            'subname': 'Qiymat o\'zgarishi',
        },
        'tr': {
            'name': 'Ayarlar',
            'subname': 'Değerlerin değiştirilmesi',
        },
    }

    return f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>'


def msg_settings_change_market(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Изменение рынка',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Change market',
        },
        'uz': {
            'name': 'Sozlamalar',
            'subname': 'Bozordagi o\'zgarishlar',
        },
        'tr': {
            'name': 'Ayarlar',
            'subname': 'Piyasa değiştirilmes',
        },
    }

    return f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>'


def msg_dop_settings(user_id: int, output: Literal['text', 'photo'], risk_upd: bool):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Дополнительные настройки',
            'output': 'Здесь вы можете настроить тип вывод расчёта',
            'text': 'текст',
            'photo': 'картинка',
            'risk': 'А также функцию изменения риска в момент расчёта',
            'on': 'включено',
            'off': 'выключено'
        },
        'en': {
            'main': 'Extra settings',
            'output': 'Here you can set up the type of calculation output',
            'text': 'text',
            'photo': 'image',
            'risk': 'As well as the function of risk change at the moment of calculation',
            'on': 'on',
            'off': 'off'
        },
        'uz': {
            'main': 'Qo\'shimcha Sozlamalar',
            'output': 'Bu yerda siz hisoblash chiqishi turini o\'rnatishingiz mumkin',
            'text': 'matn',
            'photo': 'rasm',
            'risk': 'Shuningdek, hisoblash paytida xavf o\'zgarishi funktsiyasi',
            'on': 'Kiritilgan',
            'off': 'o\'chirilgan',
        },
        'tr': {
            'main': 'Ekstra ayarlar',
            'output': 'Burada hesaplama çıktısının türünü ayarlayabilirsiniz',
            'text': 'metin',
            'photo': 'görüntü',
            'risk': 'Hesaplama anında risk değişiminin işlevi kadar',
            'on': 'Etkin',
            'off': 'kapalı',
        },
    }

    return f"""<b><u>{texts[lang]['main']}</u></b>

{texts[lang]['output']}
{txt_current_value(lang)}: <b>{texts[lang][output]}</b>

{texts[lang]['risk']}
{texts[lang]['current']}: <b>{texts[lang]['on' if risk_upd else 'off']}</b>"""


def msg_summury_profit_settings(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)
    tp_ratio = u_base.tp_ratio if (u_base is not None) else []
    split_values = u_base.split_values if (u_base is not None) else None

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Деление профита',
            'take_profit': 'Ваш тейк-профит',
            'split': 'Разделение',
            'on': 'включено',
            'off': 'выключено',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Profit division',
            'take_profit': 'Your take profit',
            'split': 'Splitting',
            'on': 'turned on',
            'off': 'turned off',
        },
        'uz': {
            'name': 'Sozlamalari',
            'subname': 'Daromad taqsimoti',
            'take_profit': 'Sizning daromadingiz',
            'split': 'Ajratish',
            'on': 'Kiritilgan',
            'off': 'o\'chirilgan',
        },
        'tr': {
            'name': 'Ayarlar',
            'subname': 'Kâr paylaşımı',
            'take_profit': 'Take profitiniz',
            'split': 'Bölme',
            'on': 'Etkin',
            'off': 'kapalı',
        },
    }

    info_result = ''

    if split_values is not None and len(split_values) != 0:
        on_off = "on"

        for i, el in enumerate(tp_ratio):
            info_result += f'<b>x{el} ({split_values[i]}%)</b>'

            if i == len(tp_ratio) - 1:
                pass
            elif i % 3 != 2:
                info_result += ' - '
            else:
                info_result += '\n'
    else:
        on_off = "off"

        info_result = f'{texts[lang]["take_profit"]}: '
        for i, el in enumerate(tp_ratio):
            info_result += f'<b>x{el}</b>'
            if i != len(tp_ratio) - 1:
                info_result += ' - '

    return f"""
⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>

{texts[lang]["split"]}: <b>{texts[lang][on_off]}</b>
{info_result}
"""


def msg_exchange(user_id: int, exchange: tuple[str, float] | None = None):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Настройки биржи',
            'now': 'Текущая',
            'fee': 'Комиссии',
        },
        'en': {
            'main': 'Exchange settings',
            'now': 'Current',
            'fee': 'Fees',
        },
        'uz': {
            'main': 'Sozlamalarni almashish',
            'now': 'Hozirgi',
            'fee': 'Komissiyalar',
        },
        'tr': {
            'main': 'Borsa ayarları',
            'now': 'Cari',
            'fee': 'Komisyonlar',
        },
    }

    current = ''
    if exchange is not None:
        current = f"""\n\n{texts[lang]["now"]}: <b>{exchange[0]}</b>
{texts[lang]["fee"]}: <b>{exchange[1] or 0}</b>"""

    return f"""<b><u>{texts[lang]['main']}</u></b>{current}"""


def msg_maker_or_taker(user_id: int, maker_fee: float, taker_fee: float):
    lang = get_lang(user_id)

    texts = {
        'ru': f'Выберите тип мейкер ({maker_fee} %) или тейкер ({taker_fee} %)',
        'en': f'Choose the type maker ({maker_fee} %) or taker ({taker_fee} %)',
        'uz': f'Ishlab chiqaruvchi ({maker_fee} %) yoki oluvchi ({taker_fee} %) turini tanlang',
        'tr': f'Yapıcı ({maker_fee} %) veya alıcı ({taker_fee} %) türünü seçin',
    }

    if lang == 'ru':
        info = """<b>Мейкеры</b> - это трейдеры, которые создают ордера и размещают их книге ордеров, ожидая, пока их выполнят другие.
<b>Тейкеры</b> - это трейдеры, которые принимают существующие ордера из книги заявок.
<i>Основное различие между ними заключается в том, что мейкеры предоставляют ликвидность, а тейкеры ее потребляют.</i>"""
    elif lang == 'uz':
        info = """<b>Meykerlar</b> - bu buyurtmalar yaratadigan va ularni buyurtmalar kitobiga joylashtiradigan, boshqalarning ularni to'ldirishini kutadigan savdogarlar.
<b>Qabul</b> qiluvchilar buyurtmalar kitobidan mavjud buyurtmalarni qabul qiladigan treyderlardir.
<i>Ikkala o'rtasidagi asosiy farq shundaki, ishlab chiqaruvchilar likvidlikni ta'minlaydilar, qabul qiluvchilar esa uni iste'mol qiladilar.</i>"""
    elif lang == 'tr':
        info = """<b>Yapımcılar</b>, emir oluşturup bunları emir defterine yerleştiren ve başkalarının bunları doldurmasını bekleyen tüccarlardır.
<b>Alıcılar</b>, emir defterinden mevcut emirleri kabul eden tüccarlardır.
<i>İkisi arasındaki temel fark, yapıcıların likidite sağlaması, alıcıların ise tüketmesidir.</i>"""
    else:
        info = """<b>Makers</b> are traders who create orders and place them in the order book, waiting for others to execute them.
<b>Takers</b> are traders who take existing orders from the order book.
<i>The main difference between the two is that makers provide liquidity while takers consume it.</i>"""

    return f"""{texts[lang]}

{info}"""


def msg_enter_exchange(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Выберите <b>биржу</b> или введите свою',
        },
        'en': {
            'main': 'Select the <b>exchange</b> or enter your own',
        },
        'uz': {
            'main': 'Birjani tanlang yoki o\'zingiznikini kiriting',
        },
        'tr': {
            'main': 'Borsa seçin veya kendinizinkini girin',
        },
    }

    return f'👉 {texts[lang]["main"]}'


def msg_enter_exchange_not_found(user_id: int, is_diff=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Данная биржа не найдена',
            'info': 'Попробуйте снова',
            'info_diff': 'Может быть вы имели в виду',
        },
        'en': {
            'main': 'This exchange was not found',
            'info': 'Try again',
            'info_diff': ' Maybe you meant',
        },
        'uz': {
            'main': 'Ushbu almashinuv topilmadi',
            'info': 'Qayta urinib ko\'ring',
            'info_diff': ' Balki siz nazarda tutgandirsiz',
        },
        'tr': {
            'main': 'Bu değişim bulunamadı',
            'info': 'Tekrar dene',
            'info_diff': ' Belki demek istedin',
        },
    }

    return f'{texts[lang]["main"]}. {texts[lang]["info_diff" if is_diff else "info"]}:'


def msg_choose_exchange_level(user_id: int, fees: list[tuple[str, float, float]]):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Выберите один из уровней',
            'fee': 'Комиссия мейкера/тейкера ',
        },
        'en': {
            'main': 'Choose one of the levels',
            'fee': 'level - fee maker/taker',
        },
        'uz': {
            'main': 'Darajalardan birini tanlang',
            'fee': 'Ishlab chiqaruvchi / oluvchi haqi',
        },
        'tr': {
            'main': ' Seviyelerden birini seçin',
            'fee': 'Yapıcı/alıcı komisyonu',
        },
    }

    levels = f'\n\n<i>{texts[lang]["fee"]} (%)</i>'
    for el in fees:
        levels += f'\n{el[0]} - <b>{el[1]}/{el[2]}</b>'

    return f'👉 {texts[lang]["main"]}' + levels


def msg_enter_fee(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': f'Введите значение <b>комисии</b>',
        'en': f'Enter value of <b>fee</b>',
        'uz': f'Komissiya qiymatini kiriting',
        'tr': f'Komisyon değerini girin',
    }

    return f'👉 {texts[lang]}:'


def msg_support(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Чтобы связаться с тех. поддержкой, нажмите на кнопку ниже',
        'en': 'To contact the customer support, click on the button below',
        'uz': 'Texnik yordam bilan bog\'lanish uchun quyidagi tugmani bosing',
        'tr': 'Teknik destek ile iletişime geçmek için aşağıdaki butona tıklayın',
    }

    return f'{texts[lang]}👇'


def msg_stats_page(user_id: int, count: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Статистика',
            'count': 'Всего расчетов',
        },
        'en': {
            'main': 'Stats',
            'count': 'All calculations done',
        },
        'uz': {
            'main': 'Statistika',
            'count': 'Jami hisob-kitoblar',
        },
        'tr': {
            'main': 'İstatistikler',
            'count': 'Toplam hesaplamalar',
        },
    }

    return f"""📊 <b><u>{texts[lang]['main']}</u></b>

{texts[lang]['count']}: <b>{count}</b>
"""


def msg_market_stats(user_id: int, market: MARKETS_TYPE, stats: CalculatorStats):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Статистика',
            'all': 'Всего расчетов',
            'tp': 'Тейк-профит',
            'sl': 'Стоп-лосс',
            'saved': 'Сохраненных',
            'sum': 'Сумма',
            'pieces': 'шт.',
            'max_profit': 'Крупный профит',
            'min_loss': 'Крупный убыток',
        },
        'en': {
            'name': 'Stats',
            'all': 'Total calculations',
            'tp': 'Take profit',
            'sl': 'Stop loss',
            'saved': 'Saved',
            'sum': 'Summary',
            'pieces': '',
            'max_profit': 'Max profit',
            'min_loss': 'Min loss',
        },
        'uz': {
            'name': 'Statistika',
            'all': 'Jami hisob-kitoblar',
            'tp': 'Foyda olish',
            'sl': 'Yo\'qotishni to\'xtatish',
            'saved': 'Saqlangan',
            'sum': 'Yig\'indi',
            'pieces': 'dona',
            'max_profit': 'Katta foyda',
            'min_loss': 'Katta yo\'qotish',
        },
        'tr': {
            'name': 'İstatistikler',
            'all': 'Toplam hesaplamalar',
            'tp': 'Take profit',
            'sl': 'Stop loss',
            'saved': 'Kaydedildi',
            'sum': 'Tutar',
            'pieces': 'adet',
            'max_profit': 'Kaydedildi',
            'min_loss': 'Büyük kayıp',
        },
    }

    return f"""📊 <b>{texts[lang]['name']}</b> - <u><b>{market_translates[lang][market]}</b></u>

{POINT} {texts[lang]['all']}: <b>{stats.all_stats_count} {texts[lang]['pieces']}</b>

{POINT} {texts[lang]['saved']}: <b>{stats.saved_stats_count} {texts[lang]['pieces']}</b>
{POINT} {texts[lang]['tp']}: <b>{stats.tp_count}</b>
{POINT} {texts[lang]['sl']}: <b>{stats.sl_count}</b>

{POINT} {texts[lang]['max_profit']}: <b>{get_print_float(stats.max_profit, 3)} {stats.currency}</b>
{POINT} {texts[lang]['min_loss']}: <b>{get_print_float(stats.min_loss, 3)} {stats.currency}</b>

{POINT} {texts[lang]['sum']}: <b>{get_print_float(stats.profit, 3)} {stats.currency}</b>
"""


def msg_freeze_calc(user_id: int, risk_value: str):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'Вы превысили суточный процент риска на',
            '2': 'Желаете приостановить торговлю на некоторое время?',
            'end': 'На это время расчеты в калькуляторе невозможно будет совершать для безопасности Вашей торговли',
        },
        'en': {
            '1': 'You have exceeded the daily percentage of risk by',
            '2': 'Would you like to suspend trading for a while?',
            'end': 'At this time, calculations in the calculator cannot be done for the safety of your trade',
        },
        'uz': {
            '1': 'Siz kunlik xavf foizidan oshib ketdingiz',
            '2': 'Savdoni bir muddat to\'xtatmoqchimisiz?',
            'end': 'Bu vaqt ichida kalkulyatorda hisob-kitoblar sizning savdolaringiz xavfsizligi uchun mumkin bo\'lmaydi',
        },
        'tr': {
            '1': 'Günlük risk yüzdesini aştınız',
            '2': 'İşlemleri bir süreliğine duraklatmak ister misiniz?',
            'end': 'Bu süre zarfında işlemlerinizin güvenliği açısından hesap makinesinde hesaplama yapmak mümkün olmayacaktır',
        }
    }

    return f"""⚠️ {texts[lang]['1']} {risk_value}.
<b>{texts[lang]['2']}</b>

{get_freeze_annotation(lang)}

{texts[lang]['end']}.
"""


def msg_stop_page(user_id: int, stop_type: str | None, is_update_deposit=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': "Выберите вид риска",
            'value': "Текущий",

            'fd': "от депозита",
            'default': "Обычный",
        },
        'en': {
            'main': "Choose the type of risk",
            'value': "Current",

            'fd': "from the deposit",
            'default': "Default",
        },
        'uz': {
            'main': "Xavf turini tanlang",
            'value': "Hozirgi",

            'fd': "Omonatdan",
            'default': "Oddiy",
        },
        'tr': {
            'main': "Bir tür risk seçin",
            'value': "Akım",

            'fd': "depozitodan",
            'default': "Sıradan",
        },
    }

    if is_update_deposit:
        stop_show = texts[lang]['fd']
    elif stop_type is None:
        stop_show = '-'
    elif stop_type == 'default':
        stop_show = texts[lang]['default']
    elif stop_type == 'atr':
        stop_show = 'ATR'
    else:
        _, percent = stop_type.split('+')
        stop_show = f'{percent}% of ATR'

    return f"""{texts[lang]['main']}
{texts[lang]['value']}: <b>{stop_show}</b>"""

# Первые сообщения


def msg_welcome(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        return f"""Используйте калькулятор для точных расчетов входа/выхода из сделок"""
    elif lang == 'uz':
        return f"""Tranzaktsiyalardan kirish/chiqish uchun aniq hisoblash uchun kalkulyatordan foydalaning"""
    elif lang == 'tr':
        return """İşlemlerden doğru giriş/çıkış hesaplamaları için bir hesap makinesi kullanın"""
    else:
        return """Use a calculator for accurate calculations of entry/exit from transactions"""

    if lang == 'ru':
        return f"""Этим калькулятором пользуются уже 15 000 человек по всему миру.

Нужен для управления риском во время торговли.

Трейдеры рискуют не более <b>1-2% депозита</b> на каждую сделку.

<i>на примере акций Газпром: </i>

<b>Ваш</b> <b>депозит</b>: 100 000 руб
<b>Риск</b>: 1% (1 000 руб)
<b>Цена за акцию</b>: 125 руб
<b>Стоп</b>: 120 руб

👉Вопрос

Сколько нужно купить акций, чтобы при цене 120, убыток составлял только 1 000 руб из 100 000 руб?

Калькулятор рассчитал:
<b>200 акций.</b>

Высчитывает и ближайшие тейк-профиты, где фиксируется прибыль.

<b>Попробуйте теперь Вы.</b>"""
    else:
        return """This calculator is already used by 15,000 people around the world. 

It is intended for managing risk while trading.

Traders risk no more than <b>1-2% of their deposit</b> on each trade.

<i>On the example of Amazon shares: </i>

<b>Your deposit</b>: 100,000 USD
<b>Risk</b>: 1% (1 000 USD)
<b>Price per share</b>: 185 USD
<b>Stop loss</b>: 180 USD

👉Question

How many shares should you buy so that at the price of 180, the loss is only 1,000 USD out of 100,000 USD?

The calculator has figured out:
<b>200 shares.</b>

It also calculates the nearest take profit where the profit is fixed.

<b>Try it now.</b>"""


def msg_after_first_settings(user_id: int, dep: float, currency: str, market: MARKETS_TYPE):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'market': 'Рынок',
            'dep': 'Депозит',
            'risk': 'Риск на сделку'
        },
        'en': {
            'market': 'Market',
            'dep': 'Deposit',
            'risk': 'Trade risk'
        },
        'uz': {
            'market': 'Bozor',
            'dep': 'Depozit',
            'risk': 'Savdo xavfi'
        },
        'tr': {
            'market': 'Pazar',
            'dep': 'Depozito',
            'risk': 'Ticaret riski'
        },
    }

    return f"""<b>{texts[lang]['market']}</b>: {market_translates[lang][market]}
<b>{texts[lang]['dep']}</b>: {dep} {currency}"""


def msg_success_base_set(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'Базовые значения сохранены',
            '2': 'Поменять их можно в настройках'
        },
        'en': {
            '1': 'The basic data have been saved',
            '2': 'You can change them in the settings'
        },
        'uz': {
            '1': 'Asosiy qiymatlar saqlangan',
            '2': 'ularni sozlamalarda o\'zgartirishingiz mumkin'
        },
        'tr': {
            '1': 'Temel değerler kaydedildi',
            '2': 'Bunları ayarlardan değiştirebilirsiniz'
        },
    }

    return f"""
✅ {texts[lang]["1"]}!
{texts[lang]["2"]} ⚙️
"""


# Базовые
def msg_success_edit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Изменения сохранены',
        'en': 'Changes have been saved',
        'uz': 'o\'zgarishlar saqlandi',
        'tr': 'Değişiklikler kaydedildi',
    }

    return f'✅ {texts[lang]}!'


def msg_frozen(user_id: int, datetime: str):
    lang = get_lang(user_id)

    text = {
        'ru': 'Калькулятор заморожен до',
        'en': 'The calculator is frozen until',
        'uz': 'Kalkulyator qotib qolgan',
        'tr': 'Hesap makinesi tarihine kadar donduruldu',
    }

    return f'❄️ {text[lang]} <b>{datetime}</b>'


# Ошибки ввода данных
def msg_trading_style_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите стиль текстом',
        'en': 'Enter the trading style in words',
        'uz': 'Uslubni matn bilan kiriting',
        'tr': 'Stili metin olarak girin',
    }

    return f'❗️ {texts[lang]}:'


def msg_freeze_error(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'Неверный формат',
        'en': 'Wrong format',
        'uz': 'Noto\'gri shakl',
        'tr': 'Yanlış biçim',
    }

    return f"""❗️ {text[lang]}
{get_freeze_annotation(lang)}
"""


def msg_pair_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валютную пару в формате XXX/XXX (только латиницей)',
        'en': 'Enter the currency pair in XXX/XXX (only in Latin)',
        'uz': 'Valyuta juftligini tanlang XXX/XXX',
        'tr': 'Döviz çiftini girin XXX/XXX',
    }

    return f'❗️ {texts[lang]}:'


def msg_pair_not_found(user_id: int, pair: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Извините. Кросс валютные расчеты сейчас недоступны',
        'en': 'Sorry. Cross currency calculations are not available now',
        'uz': 'Kechirasiz. Xoch valyuta hisob-kitoblari endi mavjud emas',
        'tr': 'Affedersiniz. Çapraz döviz işlemleri şu anda kullanılamıyor',
    }

    return f'❗️ {texts[lang]} {pair}:'


def msg_digit_error(user_id: int, value_from: int | None = None, value_to: int | None = None):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Введите значение числом',
            'from': 'от',
            'to': 'до',
        },
        'en': {
            'main': 'Enter the value in number',
            'from': 'from',
            'to': 'to',
        },
        'uz': {
            'main': 'raqam kiriting',
            'from': 'dan',
            'to': 'gacha',
        },
        'tr': {
            'main': 'Bir sayı girin',
            'from': 'dan',
            'to': 'kadar',
        },
    }

    from_txt = ''
    to_txt = ''
    if value_from is not None:
        from_txt = f' {texts[lang]["from"]} {value_from}'

    if value_to is not None:
        to_txt = f' {texts[lang]["to"]} {value_to}'

    return f'❗️ {texts[lang]["main"]}{from_txt}{to_txt}:'


def msg_text_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите значение текстом',
        'en': 'Enter the value in words',
        'uz': 'Matnga qiymat kiriting',
        'tr': 'Değeri metin olarak girin',
    }

    return f'❗️ {texts[lang]}:'


def msg_latin_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Допустимы только латинские символы',
        'en': 'Only latin characters are allowed',
        'uz': 'Faqat lotin belgilariga ruxsat beriladi',
        'tr': 'Yalnızca Latin karakterlerine izin verilir',
    }

    return f'❗️ {texts[lang]}:'


def msg_percent_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите число (от 0 до 100)',
        'en': 'Enter a number (from 0 to 100)',
        'uz': '(0 dan 100 gacha) raqam kiriting',
        'tr': 'Bir sayı girin (0\'dan 100\'e kadar)',
    }

    return f'❗️ {texts[lang]}:'


def msg_sl_op_equal_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Цена стоп-лосса и входа равны',
        'en': 'The price of the stop loss and entry are equal',
        'uz': 'Stop loss va chiqish narxlari teng',
        'tr': 'Stop loss ve giriş fiyatları eşittir',
    }

    return f'⚠️ {texts[lang]}:'


def msg_currency_error(user_id: int, type: Literal['', 'not_found'] = ''):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'enter': 'Введите валюту текстом',
            'not_found': 'Валюта не найдена'
        },
        'en': {
            'enter': 'Enter the currency in words',
            'not_found': 'The currency is not found'
        },
        'uz': {
            'enter': 'Matnga valyutani kiriting',
            'not_found': 'Valyuta topilmadi'
        },
        'tr': {
            'enter': 'Para birimini metin olarak girin',
            'not_found': 'Para birimi bulunamadı'
        },
    }

    error_mes = ''
    if type == 'not_found':
        error_mes = texts[lang]['not_found']

    return f"""{error_mes}
❗️ {texts[lang]['enter']}:
"""


def msg_splitting_error(user_id: int, error: Literal['digit', 'sum']):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'digit': 'Введите процент в виде числа',
            'sum': 'Суммарный процент превысил 100',
        },
        'en': {
            'digit': 'Enter the percent in number',
            'sum': 'The total percent has exceeded 100',
        },
        'uz': {
            'digit': 'Raqam sifatida foizni kiriting',
            'sum': 'Umumiy foiz 100 dan oshdi',
        },
        'tr': {
            'digit': 'Yüzdeyi sayı olarak girin',
            'sum': 'Toplam yüzde 100\'ü aştı',
        },
    }

    return f'❗️ <i>{texts[lang][error]}</i>'


# Калькулятор
def msg_calculate(bot: TeleBot, user_id: int, chat_id: int, is_try=False):
    lang = get_lang(user_id)

    with bot.retrieve_data(user_id, chat_id) as data:
        updated_risk = data.get('updated_risk') or 1.
        type = data.get('calc_type')
        ticker = data.get('ticker')
        open_price = data.get('open_price')
        forex: ForexInfo | None = data.get('forex')
        tool: str = data.get('tool') or ''
        deposit: float | None = data.get('deposit')
        risk: tuple[float, bool] | None = data.get('risk')
        currency: str | None = data.get('currency')
        trading_type: TRADING_TYPE = data.get('trading_type', 'margin')

    risk_value = risk[0] if (risk is not None) else None
    if (risk is not None) and risk[1] and (deposit is not None):
        risk_value = risk[0] * deposit * 0.01 * updated_risk

    type_list = ['ticker', 'dep', 'risk', 'open']
    vars_dict = {
        'ticker': ticker,
        'dep': deposit,
        'risk': risk_value,
        'open': open_price,
    }

    point = {
        'ru': {
            'ticker': 'Тикер',
            'dep': 'Депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена входа',
            'pair': 'Валютная пара',

            'trading_type': 'Тип торговли',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Deposit',
            'risk': 'Deal risk',
            'open': 'Open price',
            'pair': 'Currency pair',

            'trading_type': 'Trading type',
        },
        'uz': {
            'ticker': 'Ticker',
            'dep': 'Depozit',
            'risk': 'Risk',
            'open': 'Narxi',
            'pair': 'Valyuta juftligi',

            'trading_type': 'Savdo turi',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Depozito',
            'risk': 'Risk',
            'open': 'Fiyat',
            'pair': 'Para çifti',

            'trading_type': 'Ticaret türü',
        },
    }

    pair = '/'.join(forex.pair) if (forex is not None) else ''
    text = ''

    if type == 'forex' and pair != '':
        text += f'<b><u>{pair}</u></b>'
    elif type == 'crypto' and tool != '':
        text += f'<b><u>{tool}</u></b>'
    text += f' - {market_translates[lang].get(type, "")} {"(demo)" if is_try else ""}\n\n'

    for el in type_list:
        item = vars_dict[el]
        if item is not None:
            if item == 'ticker':
                text += f'<b>{point[lang][el]}</b>: {item}\n'
            else:
                text += ''.join((
                    f'<b>{point[lang][el]}</b>: ',
                    f'{item} ',
                    (currency or '') if (
                        type != 'forex' or forex is None) else forex.pair[1],
                    '\n'
                ))

    if not is_try:
        text += f'\n<b>{point[lang]["trading_type"]}</b>: {trading_type_translates[lang][trading_type]}\n'

    text += '\n'
    return text


def msg_calculation(user_id: int, calc: Calculation, is_try=False):
    lang = get_lang(user_id)

    is_saved = calc.in_stat
    calc_result = calcService.get_result(calc)

    texts = {
        'ru': {
            'dep': 'Депозит' if not is_saved else 'Итоговый депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена',
            'sl': 'Стоп',

            'conclusion': 'Тейк-профит',
            'profit': 'Прибыль' if not is_saved else 'Прибыль от сделки',
            'buy': 'Купите' if not is_saved else 'Было куплено',
            'sum': 'Сумма покупки',
            'style': 'Стиль торговли',
            'trading_type': 'Тип торговли',

            'coin': 'монет',
            'paper': 'акций',
            'lot': 'лота',

            'takes': 'Тейки',
            'stops': 'Стопы',

            'to': 'к',

            'fee': 'Комиссия биржи'
        },
        'en': {
            'dep': 'Deposit' if not is_saved else 'Final deposit',
            'risk': 'Deal risk',
            'open': 'Price',
            'sl': 'Stop loss',

            'conclusion': 'Take profit',
            'profit': 'Profit' if not is_saved else 'Deal profit',
            'buy': 'Buy' if not is_saved else 'Bought',
            'sum': 'Sum',
            'style': 'Trading style',
            'trading_type': 'Trading type',

            'coin': 'coins',
            'paper': 'shares',
            'lot': 'lots',

            'takes': 'Take profits',
            'stops': 'Stop losses',

            'to': 'to',

            'fee': 'Exchange fee'
        },
        'uz': {
            'dep': 'Depozit' if not is_saved else 'Yakuniy depozit',
            'risk': 'Risk',
            'open': 'Narxi',
            'sl': 'Stop loss',

            'conclusion': 'Foyda oling',
            'profit': 'Profit' if not is_saved else 'Bitim profit',
            'buy': 'Sotib oling' if not is_saved else 'Sotib oling',
            'sum': 'So\'m',
            'style': 'Savdo uslubi',
            'trading_type': 'Savdo turi',

            'coin': 'tangalar',
            'paper': 'ulushlar',
            'lot': 'juda ko\'p',

            'takes': 'Qabul qilish',
            'stops': 'To\'xtash-yo\'qotishlar',

            'to': 'ga',

            'fee': 'BIRJA BERISH'
        },
        'tr': {
            'dep': 'Depozito' if not is_saved else 'Son depozito',
            'risk': 'Risk',
            'open': 'Fiyat',
            'sl': 'Stop loss',

            'conclusion': 'Take profit',
            'profit': 'Kâr' if not is_saved else 'Anlaşmak Kâr',
            'buy': 'Satın almak' if not is_saved else 'Satın alınmış',
            'sum': 'Meblağ',
            'style': 'Ticaret tarzı',
            'trading_type': 'Ticaret türü',

            'coin': 'madeni para',
            'paper': 'hisse senetleri',
            'lot': 'çok',

            'takes': 'Karmaşa',
            'stops': 'Durma',

            'to': 'ile',

            'fee': 'Borsa ücreti'
        },
    }

    attention = ''
    count_zero = 0
    for el in calc_result.tp_values:
        if el == 0:
            count_zero += 1

    if count_zero > calc_result.tp_count // 2:
        attention = '\n⚠️ При текущих значениях стоп-лосса и цены входа, тейк‑профит равен нулю, что делает сделку некорректной.'
        attention += '\n<b>Рекомендуем</b> изменить цену входа или стоп-лосс\n'

    if calc.market == 'crypto':
        tool_name = texts[lang]["coin"]
    elif calc.market == 'forex':
        tool_name = texts[lang]["lot"]
    else:
        tool_name = texts[lang]["paper"]

    if calc.open_price > calc.stop_loss:
        long_short = 'long'
    else:
        long_short = 'short'

    # Валюта торговли
    trading_currency = calc.currency
    tool = calc.tool or ''
    if calc.forex_info is not None and calc.market == 'forex':
        trading_currency = calc.forex_info.pair[1]
        tool = ''.join(calc.forex_info.pair)

    trading_style_type = ''
    if not is_try:
        trading_style_type = f'<b>{texts[lang]["trading_type"]}</b>: {trading_type_translates[lang][calc.trading_type]}\n'
        if calc.trading_style is not None:
            trading_style_type += f'<b>{texts[lang]["style"]}</b>: {calc.trading_style.capitalize()}\n'

    # Округление
    round_count = calc.round_count or 5
    price_round_count = max(
        get_decimal_count(calc.open_price),
        get_decimal_count(calc.stop_loss),
        round_count
    )

    # Кол-во и сумма покупки
    count_bet, value_bet = calc_result.count_bet, calc_result.value_bet

    fee_text = ''
    if calc_result.fee is not None:
        fee_text = f'<b>{texts[lang]["fee"]}</b>: {get_print_float(calc_result.fee, round_count)} {calc.currency}\n'

    if is_saved:
        saved_mes = '#saved '

        stats = calcService.get_stats(user_id, calc.market)
        profit = calc.profit or 0.
        profit_result = f"""<b>{texts[lang]['profit']}: </b>{get_print_float(profit, round_count)} {calc.currency}

<b>{texts[lang]['takes']}</b>: {stats.tp_count}
<b>{texts[lang]['stops']}</b>: {get_print_float(stats.sl_count)}"""
    else:
        saved_mes = ''

        p_show = ''
        conclusion = ''
        for i in range(calc_result.tp_count):
            tp_ratio = calc.tp_ratio[i]
            tp_val = calc_result.tp_values[i]
            p_val = calc_result.profit_values[i]

            if tp_val == 0:
                if lang == 'ru':
                    conclusion += f'Тейк-профит ({tp_ratio} {texts[lang]["to"]} 1) не может быть рассчитан'
                elif lang == 'uz':
                    conclusion += f'Foyda oling ({tp_ratio} {texts[lang]["to"]} 1) hisoblab bo\'lmaydi'
                elif lang == 'tr':
                    conclusion += f'Fayda ({tp_ratio} {texts[lang]["to"]} 1) sayılmaz'
                elif lang == 'en':
                    conclusion += f'Take profit ({tp_ratio} {texts[lang]["to"]} 1) cannot be calculated'
            else:
                conclusion += f' <code>{get_print_float(tp_val, price_round_count)}</code> {trading_currency} | {get_print_float(p_val, round_count)} {calc.currency} ({tp_ratio} {texts[lang]["to"]} 1)'

                if calc_result.profit_rate_values is not None:
                    rate = calc_result.profit_rate_values[i]
                    conclusion += f' -- (<b>{get_print_float(count_bet * rate, 2)} {tool_name}</b>) {get_print_float(rate * 100, round_count)}%'

            if i != calc_result.tp_count - 1:
                conclusion += '\n'

        profit_result = f"""<b>{texts[lang]['conclusion']} | {texts[lang]["profit"]}</b>:
{conclusion}"""

    return '\n'.join((
        f'#<b><u>{tool.replace("/USDT", "").upper()}</u></b> ({long_short}) {saved_mes} - <b>{market_translates[lang][calc.market]}</b>',
        attention,
        f'<b>{texts[lang]["buy"]}</b>: <code>{get_print_float(count_bet, 4)}</code> {tool_name}',
        f'<b>{texts[lang]["sum"]}</b>: {get_print_float(value_bet, price_round_count)} {calc.currency}',
        f'<b>{texts[lang]["open"]}</b>: <code>{get_print_float(calc.open_price, price_round_count)}</code> {trading_currency}',
        f'<b>{texts[lang]["sl"]}</b>: <code>{get_print_float(calc.stop_loss, price_round_count)}</code> {trading_currency}',
        '',
        profit_result,
        '',
        f'<b>{texts[lang]["dep"]}</b>: {get_print_float(calc.deposit + (calc.profit or 0.))} {calc.currency}',
        f'<b>{texts[lang]["risk"]}</b>: {get_print_float(calc.risk_value)} {calc.currency} {f"{ENTER}<b>Риск в процентах</b>: {get_print_float(calc.risk_value / calc.deposit * 100, 4)}%" if is_try else ""}',
        fee_text,
        trading_style_type
    ))


def msg_channel_calculation(calc: Calculation, lang: Literal['ru', 'en'] = 'ru'):
    calc_result = calcService.get_result(calc)

    texts = {
        'ru': {
            'open': 'Цена',
            'sl': 'Стоп',

            'conclusion': 'Тейк-профит',
            'style': 'Стиль торговли',

            'to': 'к',
        },
        'en': {
            'open': 'Price',
            'sl': 'Stop loss',

            'conclusion': 'Take profit',
            'style': 'Trading style',

            'to': 'to',
        }
    }

    if calc.open_price > calc.stop_loss:
        long_short = 'long'
    else:
        long_short = 'short'

    # Валюта торговли
    trading_currency = calc.currency
    tool = calc.tool or ''
    if calc.forex_info is not None and calc.market == 'forex':
        trading_currency = calc.forex_info.pair[1]
        tool = ''.join(calc.forex_info.pair)

    trading_style_type = ''
    if calc.trading_style is not None:
        if lang != 'ru':
            result = trading_styles_translates.get(calc.trading_style)

            if result is None:
                try:
                    result = str(
                        text_editor.translator.translate(
                            calc.trading_style, 'en', 'ru'
                        ).text
                    )
                except:
                    result = calc.trading_style
        else:
            result = calc.trading_style

        trading_style_type += f'<b>{texts[lang]["style"]}</b>: {result.capitalize()}\n'

    # Округление
    round_count = calc.round_count or 5
    price_round_count = max(
        get_decimal_count(calc.open_price),
        get_decimal_count(calc.stop_loss),
        round_count
    )

    conclusion = ''
    for i in range(calc_result.tp_count):
        tp_ratio = calc.tp_ratio[i]
        tp_val = calc_result.tp_values[i]

        conclusion += f'<code>{get_print_float(tp_val, price_round_count)}</code> {trading_currency} ({tp_ratio} {texts[lang]["to"]} 1)'

        if i != calc_result.tp_count - 1:
            conclusion += '\n'

    profit_result = f"""<b>{texts[lang]['conclusion']}</b>:
{conclusion}"""

    return '\n'.join((
        f'#<b><u>{tool.replace("/USDT", "").upper()}</u></b> ({long_short}) - <b>{market_translates[lang][calc.market]}</b>',
        '',
        f'<b>{texts[lang]["open"]}</b>: <code>{get_print_float(calc.open_price, price_round_count)}</code> {trading_currency}',
        f'<b>{texts[lang]["sl"]}</b>: <code>{get_print_float(calc.stop_loss, price_round_count)}</code> {trading_currency}',
        '',
        profit_result,
        '',
        trading_style_type
    ))


def msg_calculate_delete(user_id: int, prev_message: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Хотите удалить расчёт',
        'en': 'Do you want to delete the calculation',
        'uz': 'Hisoblashni o\'chirmoqchimisiz?',
        'tr': 'Hesaplamayı silmek istiyor musunuz',
    }

    return f"""{prev_message.strip()}

{TAB}<b>{texts[lang]}</b>?"""


def msg_calculate_change(user_id: int, prev_message: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Что хотите изменить',
        'en': 'What do you want to change',
        'uz': 'Siz nimani o\'zgartirishni xohlaysiz',
        'tr': 'Neyi değiştirmek istiyorsun',
    }

    return f"""{prev_message.strip()}

{TAB}<b>{texts[lang]}?</b>"""


# Ввод данных
def msg_enter_atr_percent(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите % от ATR',
        'en': 'Enter % of atr',
        'uz': 'ATR ning% ni kiriting',
        'tr': "ATR'nin % 'in girin",
    }

    return f'👉 {texts[lang]}:'


def msg_enter_save_calc(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Как вы закрыли данную сделку?',
        'en': 'How have you closed this deal?',
        'uz': 'Bu shartnomani qanday yopdingiz?',
        'tr': 'Bu işlemi nasıl tamamladınız?',
    }

    return texts[lang]


def msg_enter_calc_image(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Загрузите свой скриншот сделки и он останется в чате навсегда',
        'en': 'Upload your screenshot of the deal and it will stay in the chat',
        'uz': 'Bitimning skrinshotini yuklang va u suhbatda qoladi',
        'tr': 'Anlaşmanın ekran görüntüsünüzü yükleyin ve sohbette kalacaktır',
    }

    return f'👉 {texts[lang]}'


def msg_enter_take_profit(user_id: int, tp_ratio: list[int]):
    lang = get_lang(user_id)

    current_tp = tp_ratio.copy()
    current_tp.sort()

    tp_count = len(current_tp)

    max_count = 5
    texts = {
        'ru': {
            'name': 'Установка тейк-профита',
            'current': 'Текущий выбор',
            'max': 'Учитывайте, что максимальный коэффициент тейк-профита',
            'max_count': f'Можно выбрать до <b>{max_count}</b> значений',
            '1': 'Выберите <b>первое</b> значение',
            'action': 'Выберите действие',
            'next': 'Выберите <b>следующее</b> значение',
        },
        'en': {
            'name': 'Installation of a take profit',
            'current': 'Current choice',
            'max': 'Keep in mind that the max take profit coefficient',
            'max_count': f'You can choose up to <b>{max_count}</b> values',
            '1': 'Select <b>the first</b> meaning',
            'action': 'Choose an action',
            'next': 'Select the <b>following</b> value',
        },
        'uz': {
            'name': 'ISozlash foyda olish',
            'current': 'Joriy tanlov',
            'max': 'E\'tibor bering, maksimal foyda koeffitsienti',
            'max_count': f'Siz <b>{max_count}</b> tagacha qiymatni tanlashingiz mumkin',
            '1': '<b>birinchi</b> degan ma\'noni tanlang',
            'action': 'Harakatni tanlang',
            'next': 'Keyingi qiymatni tanlang',
        },
        'tr': {
            'name': 'Take profit ayarı',
            'current': 'Geçerli seçim',
            'max': 'Lütfen maksimum take profit oranının olduğunu unutmayın',
            'max_count': f'En fazla <b>{max_count}</b> değer seçebilirsiniz',
            '1': '<b>İlk </b> anlamını seçin',
            'action': 'Bir Eylem Seçin',
            'next': '<b>Sonraki</b> değeri seç',
        },
    }

    text = f'<u>{texts[lang]["name"]}</u>\n'

    if tp_count != 0:
        text += f'{texts[lang]["current"]}: <b>'

        for el in current_tp:
            text += f'x{el} '

        text += '</b>\n'

    text += f'\n{texts[lang]["max"]} - <b>x10</b>\n'
    text += f'{texts[lang]["max_count"]}\n\n'

    if tp_count == 0:
        text += f'{texts[lang]["1"]}'
    elif tp_count == 5:
        text += f'{texts[lang]["action"]}'
    else:
        text += f'{texts[lang]["next"]}'

    return text


def msg_enter_splitting(user_id: int, tp_ratio: list[int], split: list[float], is_last=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Установка разделения профита',
            'current': 'Текущий выбор',
            'percent_sum': 'Суммарный процент',
            'last': 'Оставшиеся',
            'split': 'торговой позиции можно разбить',
            'info': 'Разбиение расчитает каждую из <i>n</i> частей для слудующих +1 тейк-профитов\nВыберите на <u>сколько частей</u> разделить остаток',
            '1': 'Выберите <b>первое</b> значение тейк-профита',
            'action': 'Выберите действие',
            'tp': 'Введите <b>процент вывода</b> для тейк-профита',
            'next': 'Выберите <b>следующее</b> значение тейк-профита',
        },
        'en': {
            'name': 'Setting the profit division',
            'current': 'Current choice',
            'percent_sum': 'The total percentage',
            'last': 'Remaining',
            'split': 'of trading position can be defeated',
            'info': 'Splitting calculates each of the <i>n</i> parts for the mining +1 teak profits\nSelect <u> how many parts </u> divide the balance',
            '1': 'Select <b> the first </b> take profit value',
            'action': 'Choose an action',
            'tp': 'Enter the <b> percentage of the output </b> for the take profite',
            'next': 'Select <b>the following</b> take profit value',
        },
        'uz': {
            'name': 'Foyda bo\'linmalarini sozlash',
            'current': 'Joriy tanlov',
            'percent_sum': 'Umumiy foiz',
            'last': 'Qolgan',
            'split': 'Savdo holatini mag\'lub etish mumkin',
            'info': 'Splittizatsiya har birida hisoblaydi <i>n</i> Konchilik +1 tog \'daromadlari uchun qismlar\n<u>nechta qism</u> balansni ajratib turing',
            '1': '<b>birinchi</b> olishning qiymatini tanlang',
            'action': 'Harakatni tanlang',
            'tp': '<b> Chiqish uchun </b> olingan professor uchun kiring',
            'next': 'Quyidagi <b>ni tanlang </b> olishning foydasi',
        },
        'tr': {
            'name': 'Kâr Bölümünü Belirleme',
            'current': 'Mevcut Seçim',
            'percent_sum': 'Toplam yüzde',
            'last': 'Geriye kalan',
            'split': 'ticaret pozisyonu yenilebilir',
            'info': 'Bölünme, madencilik +1 tik karı için parçaların her birini hesaplar \n seçme <u> kaç parça </u> dengeyi bölün',
            '1': '<b>İlk</b> alım karmaşası değerini seçin',
            'action': 'Bir Eylem Seçin',
            'tp': 'Varlığı almak için çıktının <b> yüzdesini </b> girin',
            'next': '<b> aşağıdaki </b> alım karmaşası değerini seçin',
        },
    }

    tp_count = len(tp_ratio)
    split_count = len(split)

    if tp_count == 0 or split_count == 0:
        sorted_tp, sorted_split = [], []
    else:
        sorted_tp, sorted_split = zip(*sorted(zip(tp_ratio, split)))

    percents_sum = sum(split)
    if abs(percents_sum - 100) < 0.2:
        percents_sum = 100

    text = f'<u>{texts[lang]["current"]}</u>\n'

    if tp_count != 0 and split_count != 0:
        text += f'\n<u>{texts[lang]["name"]}</u>: <b>\n'

        for i, el in enumerate(sorted_tp):
            try:
                percent = f'({get_print_float(sorted_split[i])}%)'
            except:
                percent = ''

            text += f'x{el} {percent}'

            if i == len(sorted_tp) - 1:
                pass
            elif i % 3 == 2:
                text += '\n'
            else:
                text += ' - '

        text += '</b>\n'
        text += f'<i>{texts[lang]["percent_sum"]}:</i> <b>{get_print_float(percents_sum)}</b>\n'

    text += '\n'
    if is_last:
        text += f'{texts[lang]["last"]} <b>{get_print_float(100-percents_sum, 2)}%</b> {texts[lang]["split"]}. '
        text += texts[lang]["info"]
    elif tp_count == 0:
        text += texts[lang]['1']
    elif tp_count == 5 or percents_sum == 100:
        text += texts[lang]['action']
    elif tp_count != split_count:
        text += f'{texts[lang]["tp"]} <b>x{tp_ratio[-1]}</b>'
    else:
        text += texts[lang]["next"]

    return text


def msg_enter_trading_type(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'main': 'Типы торговли',
            'm': '<b>Маржинальный</b>: расчеты будут производиться, включая кредитные плечи',
            's': '<b>Спотовый</b>: расчеты производятся, исходя из фиксированного депозита',
            'fd': '<b>От депозита</b>: расчеты производятся на весь депозит, не учитывая Ваш риск',
            'enter': 'Выберите тип'
        },
        'en': {
            'main': 'Trading types',
            'm': '<b>Margin</b>: calculations will be made  based on leverage',
            's': '<b>Spot</b>: calculations will be made based on a fixed deposit',
            'fd': '<b>From the deposit</b>: calculations are made for the entire deposit, not taking into account your risk',
            'enter': 'Select type'
        },
        'uz': {
            'main': 'Savdo turlari',
            'm': '<b>Marjasi</b>: hisob-kitoblar qo\'shimcha narsalarga asoslanadi',
            's': '<b>Sple</b>: hisob-kitoblar belgilangan omonat asosida amalga oshiriladi',
            'fd': '<b>Omonatdan</b>: hisob-kitoblar butun depozit uchun amalga oshiriladi, sizning xavfingizni hisobga olmagan holda',
            'enter': 'Turi-ni tanlang'
        },
        'tr': {
            'main': 'Ticaret Türleri',
            'm': '<b>Marj</b>: Hesaplamalar kaldıraç üzerine yapılacaktır.',
            's': '<b>Spot</b>: Hesaplamalar sabit bir depozitoya göre yapılacaktır.',
            'fd': '<b>Depozitodan</b>: riskinizi dikkate almayan tüm depozito için hesaplamalar yapılır',
            'enter': 'Türü seçin'
        },
    }

    return f"""<b><u>{texts[lang]['main']}</u></b>
{texts[lang]['m']}

{texts[lang]['s']}

👇 {texts[lang]['enter']}:"""


def msg_enter_summury_profit_type(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        return """Выберите вид разделения суммы:

<i>*Простой - без деления профита, продажа 100% торговой позиции
*Разделение - продажа торговой позиции разделяется на несколько тейк-профитов</i>"""
    elif lang == 'uz':
        return """Miqdorni taqsimlash turini tanlang:

<i>*Oddiy – foydani taqsimlamaslik, savdo pozitsiyasining 100% sotish
*Savdo pozitsiyasini bo'linish-sotish bir nechta olish foydasiga bo'linadi</i>"""
    elif lang == 'tr':
        return """Tutarın bölünme türünü seçin:

<i>*Basit - karı bölmeden, işlem pozisyonunun %100'ünü satma
*Bölünmüş - bir alım satım pozisyonunun satışı birkaç take profit'e bölünür</i>"""
    else:
        return """Select the type of division of the amount:

<i>*Simple - without profit division, sale 100% of the trading position
*Separation - the sale of a trading position is divided into several take profites </i>"""


def msg_enter_email(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите <b>почту</b> для получения чека после оплаты',
        'en': 'Enter <b>email</b> to receive the receipt after payment',
        'uz': 'To\'lovdan keyin kvitansiyani olish uchun <b> elektron pochta</​​b> kiring',
        'tr': 'Ödemeden sonra makbuzu almak için <b>e-posta</b> girin',
    }

    return f'👉 {texts[lang]}:'


def msg_enter_tool(user_id: int, market: MARKETS_TYPE = 'crypto'):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Напишите Ваш <b>инструмент</b>',
            'crypto': '<i>(например BTC или DOGE)</i>',
            'RF': '<i>(например GAZP или SBER)</i>',
            'USA': '<i>(например MCD или AMZN)</i>',
        },
        'en': {
            'main': 'Enter Your <b>tool</b>',
            'crypto': '<i>(ex. BTC or DOGE)</i>',
            'RF': '<i>(ex. GAZP or SBER)</i>',
            'USA': '<i>(ex. MCD or AMZN)</i>',
        },
        'uz': {
            'main': 'Asbobingizni kiriting',
            'crypto': '<i>(misol BTC yoki DOGE)</i>',
            'RF': '<i>(misol GAZP yoki SBER)</i>',
            'USA': '<i>(misol MCD yoki AMZN)</i>',
        },
        'tr': {
            'main': 'Enstrümanınızı girin',
            'crypto': '<i>(örnek BTC veya DOGE)</i>',
            'RF': '<i>(örnek GAZP veya SBER)</i>',
            'USA': '<i>(örnek MCD veya AMZN)</i>',
        },
    }

    info = ''
    if market in ('crypto', 'RF', 'USA'):
        info = '\n' + texts[lang][market]

    return f'👉 {texts[lang]["main"]}:  {info}'


def msg_enter_pair_price(user_id: int, pair: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите <b>цену пары</b>',
        'en': 'Enter <b>the price of the pair</b>',
        'uz': 'Juftlik narxini chop eting',
        'tr': 'Çiftin fiyatını girin',
    }

    return f'👉 {texts[lang]} <b>{pair}</b>'


def msg_enter_deposit(user_id: int, current: str|None=None):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Ваш <b>размер депозита</b> для торговли',
        'en': 'Your <b>deposit size</b> for trading',
        'uz': 'Depozit miqdorini kiriting',
        'tr': 'Yatırılan depozito tutarını girin',
    }

    current_value = ''
    if current is not None and current != '':
        current_value = f'\n<b>{txt_current_value(lang)}</b>:' + current

    return f'👉 {texts[lang]}?' + current_value


def msg_enter_risk_percent(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите <b>риск</b> на сделку',
        'en': 'Enter <b>risk</b> of the deal',
        'uz': 'Har bir savdo uchun <b>xavfni</b> kiriting',
        'tr': 'İşlem başına <b>riski</b> girin',
    }

    return f"""👉 {texts[lang]}

{get_risk_annotation(lang)}
"""


def msg_enter_day_risk(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Введите <b>риск на день</b>',
            'desc1': '"<b>Риск на день</b>" - процент или сумма капитала, превышая которую, система будет напоминать об этом.',
            'desc2': 'Трейдинг строится на систематической торговле, и риски на день/неделю/месяц нужно контролировать',
        },
        'en': {
            'main': 'Enter <b>daily risk</b>',
            'desc1': '"<b>Daily risk</b>" - the percentage or amount of capital, when exceeding which the system will remind you about it.',
            'desc2': 'Trading is based on systematic deals, and the risks for the day/week/month are needed to be controlled',
        },
        'uz': {
            'main': 'Kundalik xavfni kiriting',
            'desc1': 'Kundalik xavf - bu kapitalning foizi yoki miqdori bo\'lib, undan ortiq tizim buni sizga eslatadi.',
            'desc2': ' Savdo tizimli savdoga asoslanadi, kun/hafta/oy uchun xavflarni nazorat qilish kerak.',
        },
        'tr': {
            'main': '<b>Günlük riski</b> girin',
            'desc1': '"<b>Günlük risk</b>" - sermayenin yüzdesi veya miktarı, aşıldığında sistem size bunu hatırlatacaktır.',
            'desc2': 'Trading sistematik ticarete dayanır ve gün/hafta/ay risklerin kontrol edilmesi gerekir',
        },
    }

    return f""" {texts[lang]['desc1']}
{texts[lang]['desc2']}

👉 {texts[lang]['main']}
{get_risk_annotation(lang)}
"""


def msg_enter_trading_style(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'choose': 'Выберите <b>стиль торговли</b> из списка ниже',
            'enter': 'Либо введите <i>свой вариант</i>'
        },
        'en': {
            'choose': 'Select <b>trading style</b> from the list below',
            'enter': 'Or enter <i>your option</i>'
        },
        'uz': {
            'choose': 'Quyidagi ro\'yxatdan savdo uslubingizni tanlang',
            'enter': 'Yoki variantingizni kiriting'
        },
        'tr': {
            'choose': 'Aşağıdaki listeden bir <u>işlem stili</u> seçin',
            'enter': 'Veya <i>kendi seçeneğinizi</i> girin'
        },
    }

    return f"""👉 {texts[lang]['choose']}.
{texts[lang]['enter']}:
"""


def msg_enter_round_count(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Введите <b>количество знаков</b> после запятой',
            'max': '<i>Максимум</i>: <b>5</b>'
        },
        'en': {
            'main': 'Enter the <b>number of signs</b> after dot',
            'max': '<i>Max</i>: <b>5</b>'
        },
        'uz': {
            'main': 'Kasr sonini kiriting',
            'max': 'Maksimal: 5'
        },
        'tr': {
            'main': '<b>Ondalık basamak sayısını</b> girin',
            'max': '<i>Maksimum</i>: <b>5</b>'
        },
    }

    return f"""👉 {texts[lang]['main']}
{texts[lang]['max']} (0.00001)
"""


def msg_enter_currency(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите <b>валюту</b> или выберите из списка',
        'en': 'Enter the <b>currency</b> or select from the list below',
        'uz': 'Valyutani tanlang yoki roʻyxatdan tanlang',
        'tr': 'Para biriminizi girin veya listeden seçim yapın',
    }

    return f'👉 {texts[lang]}:'


def msg_enter_pair(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите <b>валютную пару</b>',
        'en': 'Enter the <b>currency pair</b>',
        'uz': 'Valyuta juftligini tanlang',
        'tr': 'Döviz çiftini girin',
    }

    return f"""👉 {texts[lang]} (XXX XXX):"""


def msg_enter_open_price(user_id: int, is_try=False):
    lang = get_lang(user_id)

    texts = {
        'ru': 'По какой цене <b>будете</b> покупать',
        'en': 'Enter the <b>opening price</b> of the deal',
        'uz': 'Savdoning ochilish narxini tanlang',
        'tr': 'İşlem açılış fiyatını girin',
    }

    return f"""👉 {texts[lang]}:"""


def msg_enter_stop_loss(user_id: int, is_try=False):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'По какой цене будете <b>фиксировать</b> убыток:'
    elif lang == 'uz':
        text = 'Stop loss narxini tanlang:'
    elif lang == 'tr':
        text = 'Stop loss fiyatını girin:'
    else:
        text = 'Enter the <b>stop loss</b> price'

    return f'👉 {text}'


def msg_enter_atr(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': "Введите цену ATR",
        'en': "Enter the price of ATR",
        'uz': "ATR narxini kiriting",
        'tr': "ATR'nin fiyatını girin",
    }

    return f'👉 {texts[lang]}'


def msg_enter_max_bar(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': "Введите максимальую цену бара",
        'en': "Bring the maximum bar price",
        'uz': "Maksimal bar narxini olib keling",
        'tr': "Maksimum çubuk fiyatını getirin",
    }

    return f'👉 {texts[lang]}'


def msg_enter_min_bar(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': "Введите минимальную цену бара",
        'en': "Bring the minimum bar price",
        'uz': "Minimal bar narxini kiriting",
        'tr': "Minimum çubuk fiyatını girin",
    }

    return f'👉 {texts[lang]}'


def msg_choose_direct(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': "Выберите направление",
        'en': "Select the direction",
        'uz': "Yo'nalishni tanlang",
        'tr': "Yönü seçin",
    }

    return f'👇 {texts[lang]}'


def msg_enter_profit_minus(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'Введите <b>убыток</b> по этой сделке:'
    elif lang == 'uz':
        text = 'Ushbu savdo uchun zararni kiriting:'
    elif lang == 'tr':
        text = 'Bu işlem için <b>zararı</b> girin:'
    else:
        text = 'Enter <b>loss</b> of this deal:'

    return f'👉 {text}'


def msg_enter_profit_sum(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'Введите <b>профит</b> по этой сделке:'
    elif lang == 'uz':
        text = 'Ushbu savdo uchun daromadni kiriting:'
    elif lang == 'tr':
        text = 'Bu işlem için <b>kârı</b> girin:'
    else:
        text = 'Enter <b>profit</b> of this deal:'

    return f'👉 {text}'


def msg_choose_lang(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Выберите язык',
        'en': 'Choose language',
        'uz': 'Tilni tanlang',
        'tr': 'Dil seç',
    }

    return f'🌐 {texts[lang]}'


def msg_update_deposit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Хотите изменять свой депозит при сохранении расчета?'
        },
        'en': {
            'main': 'Do you want to change your deposit after saving the calculation?'
        },
        'uz': {
            'main': 'Hisob-kitobni saqlagan holda omonatingizni o\'zgartirmoqchimisiz?'
        },
        'tr': {
            'main': 'Hesaplamayı kaydederken depozitonuzu değiştirmek ister misiniz?'
        },
    }

    return texts[lang]['main']


def msg_confirm_reset(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Вы действительно хотите <b>сбросить</b> все настройки',
        'en': 'Do you really want to  <b>return to default</b> settings',
        'uz': 'Haqiqatan ham barcha sozlamalarni tiklamoqchimisiz',
        'tr': 'Tüm ayarları <b>sıfırlamak</b> istediğinizden emin misiniz',
    }

    return f'⚠️ {texts[lang]}?'


def msg_calculation_saved(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Расчет сохранен',
        'en': 'The calculation has been saved',
        'uz': 'Hisoblash saqlandi',
        'tr': 'Hesaplama kaydedildi',
    }

    return f'✅ {texts[lang]}!'


def msg_calculation_deleted(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Расчёт удалён',
        'en': 'Calcultaion deleted',
        'uz': 'Hisoblash o\'chirildi',
        'tr': 'Hesaplama silindi',
    }

    return f'⭕️ {texts[lang]}!'


# Инструкция к калькулятору
msg_manual = ["""
❗️ *Как работать с калькулятором:*

*1.* Выбираете рынок, которым торгуете

Каждый из них имеет свои формулы расчетов, потому будете *внимательны.*
""",
              """
*2.* Вводите сумму депозита

Валюта может быть любая.
Это не имеет значения при подсчете.

Если считаете в рублях, то и объем укажет, исходя из этих данных.
""",
              """
*3.* Введите сумму риска.

Сумма депозита выбрана в 100 00 (пусть будет рублей)

Рекомендовано (особенно для внутридневной торговли) брать не более 1-2% на депозит

Если у Вас более 1 сделки внутри дня, то лучше разбить сумму риска на все сделки. 

*Дано:*
- депозит: 100 000 рублей
- риск в 1%: 1 000 рублей 

Если мы получаем стоп-лосс, то отдаем рынку не более 1 000 рублей 

Таким образом, математически у нас есть 100 попыток для увеличения капитала.
""",
              """
*4.* Вводите исходные данные для расчета объема

*а. Цена входа. *

место, где находится Ваш уровень, откуда Вы готовы войти в сделку (либо на покупку (лонг), либо продажу (шорт)). 

Я выставил цифру (условную) в 50 

*б. Цена стоп-лосса:* 

цена, по которой продам свой объем рынку, если цена пойдет не в нашу сторону. 

Я указал цену в *49*

стоит цене в 1 пункт сходить не в мою сторону, как сделка будет закрыта автоматически. 

*в. Цена тейк-профита:*

цена, при которой мы успешно закроем сделку, когда он дойдет до нужного нам уровня цены 

Я указал *в 55*

Теперь, когда вводные данные есть, смотрим на результат:
""",
              """
*5. Результаты: *

Видим, как система показала нам все исходные введенные данные и высчитала объем для входа в сделку

*Объем: 1 000 штук *

Теперь, когда у Вас есть такой инструмент для подсчетов, Вы всегда знаете где входить, выходить и фиксировать свой профит, предварительно зная и количество приобретенных монет/фьючерсов/акций 

Приятного использования.
"""
              ]
