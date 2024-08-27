from common.utils import get_print_float
from messages.common import ENTER, msg_risk_info, msg_current_value, msg_sended_data
from models import LANGUAGES_TYPE, MARKETS_TYPE, Calculation

from data.data import liteDb


def msg_enter_bars(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Выберите период баров',
        'en': 'Choose the bar interval',
        'uz': 'Barni tanlang',
        'tr': 'Çubuk aralığını seçin',
    }

    return f'👉 {texts[lang]}'


def msg_enter_bars_count(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Выберите <b>количество</b> последних баров <u>либо введите</u> своё значение',
        'en': 'Choose the <b>amount</b> of the latest bars <u>or enter</u> your own',
        'uz': 'So\'nggi barlar sonini tanlang yoki sizning qiymatingizni kiriting',
        'tr': 'Son çubuk sayısını seçin veya değerinizi girin',
    }

    return f'👉 {texts[lang]}'


def msg_enter_atr_percent(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите % от ATR',
        'en': 'Enter % of atr',
        'uz': 'ATR ning% ni kiriting',
        'tr': "ATR'nin % 'in girin",
    }

    return f'👉 {texts[lang]}:'


def msg_enter_save_calc(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Как вы закрыли данную сделку?',
        'en': 'How have you closed this deal?',
        'uz': 'Bu shartnomani qanday yopdingiz?',
        'tr': 'Bu işlemi nasıl tamamladınız?',
    }

    return texts[lang]


def msg_enter_calc_img_text(lang: LANGUAGES_TYPE, calc: Calculation):
    texts = {
        'ru': {
            'main': 'Опишите сделку и прикрепите картинку',
            'change': 'Отправьте новое описание и картинку для <u>изменения</u>',
            'comment': 'Напишите комментарий и добавьте график',
            'info': 'При отправке фото с комментарием предыдующая картинка будет утерена',
        },
        'en': {
            'main': 'Describe the deal and attach the picture',
            'change': 'Send a new description and picture for <u>changes</u>',
            'comment': 'Write a comment and add a schedule',
            'info': 'When sending a photo with a comment, the previous picture will be lost',
        },
        'uz': {
            'main': 'Shartni tasvirlab bering va rasmni yo',
            'change': '<u>O\'zgarishlari</u> uchun yangi tavsif va rasmni yuboring',
            'comment': 'Izoh yozing va jadval qo\'shing',
            'info': "Fotosuratni sharh bilan yuborishda oldingi rasm yo'qoladi",
        },
        'tr': {
            'main': 'Anlaşmayı tanımlayın ve resmi yoğur',
            'change': '<u>Değişiklikleri</u> için yeni bir açıklama ve resim gönderin',
            'comment': 'Bir yorum yazın ve bir program ekleyin',
            'info': 'Yorumla bir fotoğraf gönderirken, önceki resim kaybolacak',
        },
    }

    text = ''
    info = ''
    if calc.status == 'FINISH':
        text = texts[lang]['comment']
        info = f'\n<i>{texts[lang]["info"]}</i>'
    elif (calc.photo is None and calc.description is None):
        text = texts[lang]['main']
    else:
        text = texts[lang]['change']

    return f'👉 {text}' + info


def msg_enter_take_profit(lang: LANGUAGES_TYPE, tp_ratio: list[int]):
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


def msg_enter_splitting(lang: LANGUAGES_TYPE, tp_ratio: list[int], split: list[float], is_last=False):
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


def msg_enter_trading_type(lang: LANGUAGES_TYPE):
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


def msg_enter_summury_profit_type(lang: LANGUAGES_TYPE):
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


def msg_enter_email(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите <b>почту</b> для получения чека после оплаты',
        'en': 'Enter <b>email</b> to receive the receipt after payment',
        'uz': 'To\'lovdan keyin kvitansiyani olish uchun <b> elektron pochta</​​b> kiring',
        'tr': 'Ödemeden sonra makbuzu almak için <b>e-posta</b> girin',
    }

    return f'👉 {texts[lang]}:'


def msg_enter_tool(lang: LANGUAGES_TYPE, market: MARKETS_TYPE = 'crypto'):
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


def msg_enter_pair_price(lang: LANGUAGES_TYPE, pair: str):
    texts = {
        'ru': 'Введите <b>цену пары</b>',
        'en': 'Enter <b>the price of the pair</b>',
        'uz': 'Juftlik narxini chop eting',
        'tr': 'Çiftin fiyatını girin',
    }

    return f'👉 {texts[lang]} <b>{pair}</b>'


def msg_enter_deposit(lang: LANGUAGES_TYPE, current: str | None = None):
    texts = {
        'ru': 'Ваш <b>размер депозита</b> для торговли',
        'en': 'Your <b>deposit size</b> for trading',
        'uz': 'Depozit miqdorini kiriting',
        'tr': 'Yatırılan depozito tutarını girin',
    }

    current_value = ''
    if current is not None and current != '':
        current_value = f'\n<b>{msg_current_value(lang)}</b>:' + current

    return f'👉 {texts[lang]}?' + current_value


def msg_enter_market(lang: LANGUAGES_TYPE):
    info = {
        'ru': '<b>Выбирая</b> один из рынков, расчеты, функционал, статистика сделок - меняются.\n\nДля каждого рынка можете настроить свой <b>функционал</b> управления.',
        'en': 'Choosing one of the markets, the calculations, functionality, and statistics of deals change accordingly.\n\nFor each market, you can customize specific management options.',
        'uz': "Birja, hisob-kitoblar, funktsionallik, bitimlar statistikasidan birini tanlash o'zgarmoqda.\n\nHar bir bozor uchun siz o'zingizni boshqaruv funktsiyasini sozlashingiz mumkin.",
        'tr': 'Piyasalardan birini seçmek, hesaplamalar, işlevsellik, işlem istatistikleri değişiyor.\n\nHer pazar için kontrol işlevinizi yapılandırabilirsiniz.',
    }

    if lang == 'ru':
        return "👉 Выберите <b>рынок</b> торговли"
    elif lang == 'uz':
        return "👉 <b>Bozor</b> savdo-sotiqni tanlang"
    elif lang == 'tr':
        return "👉 <b>Pazar</b> ticareti seçin"
    else:
        return "👉 Select trading <b>market</b>" + f'\n\n{info[lang]}'


def msg_enter_risk_percent(lang: LANGUAGES_TYPE, is_first=False):
    info = {
        'ru': """Трейдер заранее знает о убытках.
Выберите <b>% или сумму риска</b> на каждую сделку, система возьмет на себя расчеты.

<i>например, при депозите 10 000 USD и риске в 1%, потери на каждую сделку будут 100 USD</i>""",
        'en': """The trader is aware of losses in advance.
Select the % or amount of risk for each trade, the system will take care of the calculations.

For example, with a deposit of 10 000 USD and a risk of 1%, the loss per trade will be 100 USD.""",
        'uz': """Savdogar oldindan yo'qotishlardan xabardor.
Har bir savdo uchun% yoki miqdorini tanlang, tizim hisob-kitoblarga g'amxo'rlik qiladi.

Masalan, 10 000 AQSh dollari va 1% xavfi bilan 1% xavfi bilan, har bir savdot uchun yo'qotish 100 AQSh dollarini tashkil etadi.""",
        'tr': """Tüccar önceden kayıpların farkındadır.
Her ticaret için risk % veya risk miktarını seçin, sistem hesaplamalarla ilgilenecektir.

Örneğin, 10.000 USD ve%1 riski ile ticaret başına zarar 100 USD olacaktır.""",
    }

    texts = {
        'ru': 'Введите <b>риск</b> на сделку',
        'en': 'Enter <b>risk</b> of the deal',
        'uz': 'Har bir savdo uchun <b>xavfni</b> kiriting',
        'tr': 'İşlem başına <b>riski</b> girin',
    }

    dop = ''
    if is_first:
        if lang == 'ru':
            dop = '<i>(проф трейдеры рискуют на каждую сделку не более 1% от депозита)</i>'
        elif lang == 'en':
            dop = '<i>(Professor traders risk for each transaction no more than 1% of the deposit)</i>'
        elif lang == 'uz':
            dop = '<i>(Har bir savdo uchun xavfni 1% dan oshirib bo\'lmaydi)</i>'
        elif lang == 'tr':
            dop = '<i>(Her işlem için risk %1\'den fazla olamaz)</i>'

    return f"""👉 {texts[lang]}
{dop}
{'' if is_first else f'{info[lang]}{ENTER}{ENTER}{msg_risk_info(lang)}'}
"""


def msg_enter_day_risk(lang: LANGUAGES_TYPE):
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
{msg_risk_info(lang)}
"""


def msg_enter_trading_style(lang: LANGUAGES_TYPE):
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


def msg_enter_round_count(lang: LANGUAGES_TYPE):
    info = {
        'ru': 'Округляйте вывод данных для удобства расчетов (если это требуется)',
        'en': 'Round the data output for convenient calculations (if required)',
        'uz': "Hisob-kitoblarga qulaylik yaratish uchun ma'lumotlar ishlab chiqarishni joriy qiling (agar kerak bo'lsa)",
        'tr': 'Hesaplamaların rahatlığı için verilerin çıktısını destekleyin (gerekirse)',
    }

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

    return f"""{info[lang]}

👉 {texts[lang]['main']}
{texts[lang]['max']} (0.00001)
"""


def msg_enter_currency(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите <b>валюту</b> или выберите из списка',
        'en': 'Enter the <b>currency</b> or select from the list below',
        'uz': 'Valyutani tanlang yoki roʻyxatdan tanlang',
        'tr': 'Para biriminizi girin veya listeden seçim yapın',
    }

    return f'👉 {texts[lang]}:'


def msg_enter_pair(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите <b>валютную пару</b>',
        'en': 'Enter the <b>currency pair</b>',
        'uz': 'Valyuta juftligini tanlang',
        'tr': 'Döviz çiftini girin',
    }

    return f"""👉 {texts[lang]} (XXX XXX):"""


def msg_enter_open_price(lang: LANGUAGES_TYPE, is_try=False):
    texts = {
        'ru': 'По какой цене <b>войдёте</b> в сделку',
        'en': 'Enter the <b>opening price</b> of the deal',
        'uz': 'Savdoning ochilish narxini tanlang',
        'tr': 'İşlem açılış fiyatını girin',
    }

    return f"""👉 {texts[lang]}:"""


def msg_enter_stop_loss(lang: LANGUAGES_TYPE, is_try=False, send_stat: Calculation | None = None):
    dop = ''
    if send_stat:
        dop = msg_sended_data(lang, send_stat)

    if lang == 'ru':
        text = 'По какой цене будете <b>фиксировать</b> убыток:'
    elif lang == 'uz':
        text = 'Stop loss narxini tanlang:'
    elif lang == 'tr':
        text = 'Stop loss fiyatını girin:'
    else:
        text = 'Enter the <b>stop loss</b> price'

    return f'{dop}👉 {text}'


def msg_enter_atr(lang: LANGUAGES_TYPE, send_stat: Calculation | None = None):
    dop = ''
    if send_stat:
        dop = msg_sended_data(lang, send_stat)

    texts = {
        'ru': "Введите цену ATR",
        'en': "Enter the price of ATR",
        'uz': "ATR narxini kiriting",
        'tr': "ATR'nin fiyatını girin",
    }

    return f'{dop}👉 {texts[lang]}'


def msg_enter_max_bar(lang: LANGUAGES_TYPE):
    texts = {
        'ru': "Введите максимальую цену бара",
        'en': "Bring the maximum bar price",
        'uz': "Maksimal bar narxini olib keling",
        'tr': "Maksimum çubuk fiyatını getirin",
    }

    return f'👉 {texts[lang]}'


def msg_enter_min_bar(lang: LANGUAGES_TYPE):
    texts = {
        'ru': "Введите минимальную цену бара",
        'en': "Bring the minimum bar price",
        'uz': "Minimal bar narxini kiriting",
        'tr': "Minimum çubuk fiyatını girin",
    }

    return f'👉 {texts[lang]}'


def msg_choose_direct(lang: LANGUAGES_TYPE, tg_id: int, value: float | None = None):
    atr_settings = liteDb.getUserAtrSettings(tg_id)
    period, count = atr_settings[1].split('+')

    texts = {
        'ru': "Выберите направление",
        'en': "Select the direction",
        'uz': "Yo'nalishni tanlang",
        'tr': "Yönü seçin",
    }

    atr_info = {
        'ru': f'ATR <b>{count} баров</b> ({period.upper()})',
        'en': f'ATR <b>{count} bars</b> ({period.upper()})',
        'uz': f'ATR <b>{count} bar</b> ({period.upper()})',
        'tr': f'ATR <b>{count} çubukları</b> ({period.upper()})'
    }

    avg_atr = ''
    if value is not None:
        avg_atr = f'{atr_info[lang]} ~ <b>{get_print_float(value, 5)} USDT</b>\n\n'

    return f'{avg_atr}👇 {texts[lang]}'


def msg_enter_profit_minus(lang: LANGUAGES_TYPE):
    if lang == 'ru':
        text = 'Введите <b>убыток</b> по этой сделке:'
    elif lang == 'uz':
        text = 'Ushbu savdo uchun zararni kiriting:'
    elif lang == 'tr':
        text = 'Bu işlem için <b>zararı</b> girin:'
    else:
        text = 'Enter <b>loss</b> of this deal:'

    return f'👉 {text}'


def msg_enter_profit_sum(lang: LANGUAGES_TYPE):
    if lang == 'ru':
        text = 'Введите <b>профит</b> по этой сделке:'
    elif lang == 'uz':
        text = 'Ushbu savdo uchun daromadni kiriting:'
    elif lang == 'tr':
        text = 'Bu işlem için <b>kârı</b> girin:'
    else:
        text = 'Enter <b>profit</b> of this deal:'

    return f'👉 {text}'


def msg_choose_lang(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Выберите язык',
        'en': 'Choose language',
        'uz': 'Tilni tanlang',
        'tr': 'Dil seç',
    }

    return f'🌐 {texts[lang]}'
