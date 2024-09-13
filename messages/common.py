from models import CALC_STATUS_TYPE, LANGUAGES_TYPE, MARKETS_TYPE, TRADING_TYPE, Calculation
from Classes import text_editor


POINT = '•'
TAB = '   '
ENTER = '\n'


# Переводы
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
            'в канале': 'in channel',

            'Пробой': 'Breakout',
            'Отбой': 'Bounce',
            'Ложные': 'Fakeout',
            'Скользящие': 'Moving average',
            'High/low': 'High/low',
            'В канале': 'In channel',
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

    ch_styles = ['в канале', 'В канале']
    return 'торговля внутри канала' if lang == 'ru' and trading_style in ch_styles else result


def msg_atr_bars(lang: LANGUAGES_TYPE, value: str):
    try:
        period, count = value.split('+')
    except:
        return ''

    period_show = ''
    if period == '15m':
        if lang == 'ru':
            period_show = f'15-минутных баров'
        elif lang == 'en':
            period_show = f'15-minute bars'
        elif lang == 'uz':
            period_show = f'15 daqiqa barlari'
        else:
            period_show = f'15 dakikalık barlar'
    elif period == '1h':
        if lang == 'ru':
            period_show = f'часовых баров'
        elif lang == 'en':
            period_show = f'hourly bars'
        elif lang == 'uz':
            period_show = f'saatcha barlari'
        else:
            period_show = f'saatlik barlar'
    elif period == '4h':
        if lang == 'ru':
            period_show = f'4-часовых баров'
        elif lang == 'en':
            period_show = f'4-hour bars'
        elif lang == 'uz':
            period_show = f'4 saatcha barlari'
        else:
            period_show = f'4 saatlik barlar'
    elif period == '1d':
        if lang == 'ru':
            period_show = f'дневных баров'
        elif lang == 'en':
            period_show = f'daily bars'
        elif lang == 'uz':
            period_show = f'kunlik barlari'
        else:
            period_show = f'günlük barlar'

    if period_show == '':
        return ''

    if lang == 'ru':
        return f'средний atr крайних <b>{count} {period_show}</b>'
    elif lang == 'en':
        return f'average atr of the last <b>{count} {period_show}</b>'
    elif lang == 'uz':
        return f'oxirgi ARR <b>{count} {period_show}</b>'
    else:
        return f'geçmiş <b>{count} {period_show}</b> ortalaması'


def msg_current_value(lang: LANGUAGES_TYPE):
    if lang == 'ru':
        return 'Текущее значение'
    elif lang == 'uz':
        return 'Hozirgi qiymat'
    elif lang == 'tr':
        return 'Mevcut değeri'
    else:
        return 'Current value'


def msg_risk_info(lang: LANGUAGES_TYPE):
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
{texts[lang]['2']}"""


def msg_freeze_info(lang: LANGUAGES_TYPE):
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


def msg_success_edit(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Изменения сохранены',
        'en': 'Changes have been saved',
        'uz': 'o\'zgarishlar saqlandi',
        'tr': 'Değişiklikler kaydedildi',
    }

    return f'✅ {texts[lang]}!'


def msg_sended_data(lang: LANGUAGES_TYPE, send_stat: Calculation):
    dop = ''

    short_long = 'long'
    if send_stat.openPrice < send_stat.stopLoss:
        short_long = 'short'

    if lang == 'ru':
        dop = f"""#{(send_stat.tool or '').replace('/USDT', '')} - {transl_market(send_stat.market, lang)}

Цена: {send_stat.openPrice} USDT
Направление: {short_long}"""
    elif lang == 'uz':
        dop = f"""#{send_stat.tool} - {transl_market(send_stat.market, lang)}

Narx: {send_stat.openPrice} USDT
Yo'nalish: {short_long}"""
    elif lang == 'tr':
        dop = f"""#{send_stat.tool} - {transl_market(send_stat.market, lang)}

Fiyat: {send_stat.openPrice} USDT
Yön: {short_long}"""
    else:
        dop = f"""#{send_stat.tool} - {transl_market(send_stat.market, lang)}

Price: {send_stat.openPrice} USDT
Direction: {short_long}"""
    dop += '\n\n'

    return dop


# Инструкция к калькулятору
msg_manuals = ["""
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
