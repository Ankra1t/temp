from common.dt import get_datetime_now, get_str_by_datetime
from common.utils import get_lang, get_print_float
from models import MARKETS_TYPE, CalculatorStats
from messages.common import (
    POINT, msg_freeze_info, transl_market
)


# Основные страницы
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

    return f"""📊 <b>{texts[lang]['name']}</b> - <u><b>{transl_market(market, lang)}</b></u>

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

{msg_freeze_info(lang)}

{texts[lang]['end']}.
"""


# Ввод данных?
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


def msg_violation(user_id: int, current: int, isToday: bool, messages: list[dict[str, str]], is_edit: bool):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Нарушения',
            'info': """Отмечайте, нарушали ли правила сегодня.
Если не нарушали, получите <b>5 баллов</b> за день.
В течение месяца Вы можете набрать до <b>150 баллов</b>.""",
            'edit': 'Изменять статус можно <b>4 раза</b> в месяц.',
            'current': 'За текущий месяц',
            'point': 'баллов',
            'today': 'Сегодня:',

            'True': 'нарушил',
            'False': 'не нарушил',
            'None': 'не торговал',
        },
        'en': {
            'main': 'Violations',
            'info': """Mark if the rules have violated today.
If you are not violated, get <b>5 points</b> per day.
Within a month you can score up to <b>150 points</b>.""",
            'edit': 'You can change the status <b>4 times</b> per month.',
            'current': 'For the current month',
            'point': 'points',
            'today': 'Today:',

            'True': 'violated',
            'False': 'no violate',
            'None': 'no trade',
        },
        'uz': {
            'main': 'Qoidabuzarliklar',
            'info': 'Siz bugun qoidabuzarlik qilganligingizni belgilash imkoniyatiga egasiz. Agar siz qoidabuzarlik qilmagan bo\'lsangiz, buni belgilang va kun uchun 5 ball olasiz. Oy davomida siz maksimal 150 ball to\'plashingiz mumkin.',
            'edit': 'Siz oyiga <b>4 marta</​​b> holatini o\'zgartirishingiz mumkin.',
            'current': 'Joriy oy uchun',
            'point': 'ballar',
            'today': 'Bugun:',

            'True': 'buzilgan',
            'False': 'buzilmagan',
            'None': 'savdo yo\'q',
        },
        'tr': {
            'main': 'İhlaller',
            'info': 'Bugün kuralları ihlal edip etmediğinizi işaretleyebilirsiniz. Eğer kuralları ihlal etmediyseniz, bunu işaretleyin ve gün için 5 puan kazanın. Ay boyunca maksimum 150 puan kazanabilirsiniz.',
            'edit': 'Ayda <b>4 kez</b> durumunu değiştirebilirsiniz.',
            'current': 'Mevcut ay için',
            'point': 'puan',
            'today': 'Bugün:',

            'True': 'ihlal edilen',
            'False': 'ihlal etmek yok',
            'None': 'ticaret Yok',
        }
    }

    months = {'ru': [
        'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
        'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
    ], 'en': [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]}

    mes = ''
    for el in messages:
        mes += f'\n<b>{el.get("date")}</b>'
        status = str(el.get("status"))

        points = 5 if status == 'False' else 0 if status == 'True' else 1
        mes += f' - {texts[lang][status]} ({points})'

    current_date = get_str_by_datetime(get_datetime_now(), "day.month")
    month = ('За' if lang == 'ru' else 'For') + ' ' + \
        months[lang][int(current_date.split('.')[1]) - 1]

    return f"""<b>{texts[lang]['main']} - {current_date}</b>""" \
        + (f"""\n\n{texts[lang]['info']}""" if not isToday else '') \
        + (f"""\n\n{texts[lang]['edit']}""" if is_edit else '') \
        + f"""\n\n<b>{month}</b>: {current}/150 {texts[lang]['point']}
{mes}

{texts[lang]['today'] if not isToday else ''}
"""


def msg_violation_message(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Можете описать нарушение и прикрепть фото',
        'en': 'You can describe the violation and attach a photo',
        'uz': 'Siz qoidabuzarlikni tasvirlashingiz va fotosuratni biriktirishingiz mumkin',
        'tr': 'İhlali tanımlayabilir ve bir fotoğraf ekleyebilirsiniz',
    }

    return texts[lang]


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
