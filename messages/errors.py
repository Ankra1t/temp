from typing import Literal
from messages.common import msg_freeze_info
from models import LANGUAGES_TYPE


def msg_trading_style_error(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите стиль текстом',
        'en': 'Enter the trading style in words',
        'uz': 'Uslubni matn bilan kiriting',
        'tr': 'Stili metin olarak girin',
    }

    return f'❗️ {texts[lang]}:'


def msg_freeze_error(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'Неверный формат',
        'en': 'Wrong format',
        'uz': 'Noto\'gri shakl',
        'tr': 'Yanlış biçim',
    }

    return f"""❗️ {text[lang]}
{msg_freeze_info(lang)}
"""


def msg_pair_error(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите валютную пару в формате XXX/XXX (только латиницей)',
        'en': 'Enter the currency pair in XXX/XXX (only in Latin)',
        'uz': 'Valyuta juftligini tanlang XXX/XXX',
        'tr': 'Döviz çiftini girin XXX/XXX',
    }

    return f'❗️ {texts[lang]}:'


def msg_digit_error(lang: LANGUAGES_TYPE, value_from: int | None = None, value_to: int | None = None):
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


def msg_text_error(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите значение текстом',
        'en': 'Enter the value in words',
        'uz': 'Matnga qiymat kiriting',
        'tr': 'Değeri metin olarak girin',
    }

    return f'❗️ {texts[lang]}:'


def msg_latin_error(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Допустимы только латинские символы',
        'en': 'Only latin characters are allowed',
        'uz': 'Faqat lotin belgilariga ruxsat beriladi',
        'tr': 'Yalnızca Latin karakterlerine izin verilir',
    }

    return f'❗️ {texts[lang]}:'


def msg_sl_op_equal_error(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Цена стоп-лосса и входа равны',
        'en': 'The price of the stop loss and entry are equal',
        'uz': 'Stop loss va chiqish narxlari teng',
        'tr': 'Stop loss ve giriş fiyatları eşittir',
    }

    return f'⚠️ {texts[lang]}:'


def msg_currency_error(lang: LANGUAGES_TYPE, type: Literal['', 'not_found'] = ''):
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


def msg_splitting_error(lang: LANGUAGES_TYPE, error: Literal['digit', 'sum']):
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
