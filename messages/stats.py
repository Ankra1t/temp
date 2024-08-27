from common.utils import get_print_float
from messages.common import transl_market, POINT
from models import LANGUAGES_TYPE, MARKETS_TYPE, CalculatorStats


def msg_stats_page(lang: LANGUAGES_TYPE, count: int):
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

{texts[lang]['count']}: <b>{count}</b>"""


def msg_market_stats(lang: LANGUAGES_TYPE, market: MARKETS_TYPE, stats: CalculatorStats):
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

    return f"""📊 <b>{texts[lang]['name']}</b> - <u><b>{transl_market(market, lang)}</b></u>

{POINT} {texts[lang]['all']}: <b>{stats.all_stats_count} {texts[lang]['pieces']}</b>

{POINT} {texts[lang]['saved']}: <b>{stats.saved_stats_count} {texts[lang]['pieces']}</b>
{POINT} {texts[lang]['tp']}: <b>{stats.tp_count}</b>
{POINT} {texts[lang]['sl']}: <b>{stats.sl_count}</b>

{POINT} {texts[lang]['max_profit']}: <b>{get_print_float(stats.max_profit, 3)} {stats.currency}</b>
{POINT} {texts[lang]['min_loss']}: <b>{get_print_float(stats.min_loss, 3)} {stats.currency}</b>

{POINT} {texts[lang]['sum']}: <b>{get_print_float(stats.profit, 3)} {stats.currency}</b>"""
