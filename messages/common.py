from models import CALC_STATUS_TYPE, LANGUAGES_TYPE, MARKETS_TYPE, TRADING_TYPE
from Classes import text_editor


POINT = '•'
TAB = '   '
ENTER = '\n'


def transl_market(market: MARKETS_TYPE, lang: LANGUAGES_TYPE = 'ru'):
    texts: dict[LANGUAGES_TYPE, dict[MARKETS_TYPE, str]] = {
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

    return texts.get(lang, {}).get(market, '')


def transl_tr_type(type: TRADING_TYPE, lang: LANGUAGES_TYPE = 'ru'):
    texts: dict[LANGUAGES_TYPE, dict[TRADING_TYPE, str]] = {
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

    return texts.get(lang, {}).get(type, '')


def transl_status(status: CALC_STATUS_TYPE, lang: LANGUAGES_TYPE = 'ru'):
    texts: dict[LANGUAGES_TYPE, dict[CALC_STATUS_TYPE, str]] = {
        'ru': {
            'WAIT': 'В ожидании',
            'DEAL': 'В сделке',
            'CANCEL': 'Отменён',
        },
        'en': {
            'WAIT': 'In wait',
            'DEAL': 'In deal',
            'CANCEL': 'Cancel',
        },
        'uz': {
            'WAIT': 'Kutish paytida',
            'DEAL': 'Bitim',
            'CANCEL': 'Bekor qilmoq',
        },
        'tr': {
            'WAIT': 'Beklemede',
            'DEAL': 'Anlaşma içinde',
            'CANCEL': 'İptal etmek',
        },
    }

    return texts.get(lang, {}).get(status, '')


def transl_tr_style(trading_style: str | None, lang: LANGUAGES_TYPE = 'ru'):
    if trading_style is None:
        return

    result = trading_style

    if lang != 'ru':
        texts = {
            'пробой уровня': 'breakout',
            'отбой от уровня': 'bounce',
            'ложные пробои': 'fakeout',
            'скользящие средние': 'moving average',
            'торговля на high/low': 'high/low trading',
            'Пробой': 'Breakout',
            'Отбой': 'Bounce',
            'Ложные': 'Fakeout',
            'Скользящие': 'Moving average',
            'high/low': 'high/low',
        }

        result = texts.get(trading_style, '')

        if result is None:
            try:
                result = str(
                    text_editor.translator.translate(
                        trading_style, 'en', 'ru'
                    ).text
                )
            except:
                pass

    return result
