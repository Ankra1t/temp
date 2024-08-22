from common.utils import get_print_float
from messages.common import POINT, transl_market, transl_tr_style, transl_tr_type
from models import LANGUAGES_TYPE, UserCalcSettings


def msg_settings(lang: LANGUAGES_TYPE, u_base: UserCalcSettings, is_risk_update=False):
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
                 ("%" if  u_base.risk[1] else f" {currency}")) if (u_base.risk is not None) else "-"

    show_day_risk = (f'{get_print_float(u_base.day_risk[0])}' +
                     ('%' if u_base.day_risk[1] else f' {currency}')) if (u_base.day_risk is not None) else "-"

    updating_deposit = texts[lang]['off']
    if u_base.is_updating_deposit:
        updating_deposit = texts[lang]['on']

    return f"""⚙️ <b><u>{texts[lang]["name"]}</u></b>

{POINT} {texts[lang]["market"]}: <b>{transl_market(u_base.market, lang)}</b>

{POINT} {texts[lang]["dep"]}: <b>{show_deposit} {currency}</b>
{POINT} {texts[lang]["risk"]}: <b>{show_risk}</b>
{POINT} {texts[lang]["updating_deposit"]}: <b>{updating_deposit}</b>

{POINT} {texts[lang]["trading_style"]}: <b>{transl_tr_style(u_base.trading_style, lang) or '-'}</b>
{POINT} {texts[lang]["trading_type"]}: <b>{transl_tr_type(u_base.trading_type, lang)}</b>
{POINT} {texts[lang]["tp_show"]}: <b>{tp_result}</b>

{POINT} {texts[lang]["day_risk"]}: <b>{show_day_risk}</b>
{POINT} {texts[lang]["round_count"]}: <b>{u_base.round_count or '-'}</b>

{POINT} {texts[lang]["is_risk_update"]}: <b>{texts[lang]['on'] if is_risk_update else texts[lang]['off']}</b>"""
# {POINT} {texts[lang]["output"]}: <b>{texts[lang]['by_text'] if calc_output == 'text' else texts[lang]['by_image']}</b>


def msg_deposit(lang: LANGUAGES_TYPE, u_base: UserCalcSettings | None, stop: str | None):
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

    info = {
        'ru': 'Настройте калькулятор для максимально удобного использования, начиная от депозита, заканчивая округлениями цифр и деление профита для частичного выхода из сделки(ок)',
        'en': 'Personalize the calculator for highest ease of use, from deposit to rounding figures and dividing the profit for partial exit from the trade(s).',
        'uz': "Kalkulyatorni omonatdan boshlab, raqamlarning yaxlitlanishi va qisman bitimdan qisman bo'linish bilan tugash bilan tugaydigan kalkulyatorni sozlang",
        'tr': 'Hesap makinesini, depozitten başlayarak, sayıların yuvarlanması ve işlemden kısmi çıkış için kârın bölünmesi ile biten en uygun kullanım için yapılandırın (OK)',
    }

    info_upd = {
        'ru': "При сохранении статистики по каждой сделке, депозит может автоматически изменяться (при вкл функции), рассчитывая новые сделки, исходя из действующего депозита",
        'en': "When saving statistics for each trade, the deposit can automatically change (when the function is on), calculating new trades based on the current deposit",
        'uz': "Har bir bitim bo'yicha statistikani saqlab turganda, omonat avtomatik ravishda joriy omonat asosida yangi operatsiyalarni hisoblash, yangi operatsiyalarni hisoblashi mumkin",
        'tr': "Her işlemle ilgili istatistikleri korurken, depozito otomatik olarak değişebilir (bir işlevin bir işleviyle), mevcut depozitoya dayalı yeni işlemleri hesaplayabilir",
    }

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

{info[lang]}

{POINT} {texts[lang]['dep']}: <b>{deposit} {currency}</b>
{POINT} {texts[lang]['round_count']}: <b>{round_count}</b>
{POINT} {texts[lang]['stop']}: <b>{stop_show}</b>

{POINT} {texts[lang]['update']}: <b>{texts[lang]['on'] if is_update else texts[lang]['off']}</b>
{info_upd[lang]}
"""
