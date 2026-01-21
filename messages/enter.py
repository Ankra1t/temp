from common.utils import get_print_float
from messages.common import ENTER, msg_risk_info, msg_current_value, msg_sended_data
from models import LANGUAGES_TYPE, MARKETS_TYPE, Calculation

from service import user_settings_storage


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
            'main': 'Опишите сделку и/или прикрепите картинку',
            'change': 'Отправьте новое описание и/или картинку для <u>изменения</u>',
            'comment': 'Напишите комментарий и/или добавьте график',
            'info': 'При отправке фото с комментарием предыдущая картинка будет утеряна',
        },
        'en': {
            'main': 'Describe the deal and/or attach the picture',
            'change': 'Send a new description and/or picture for <u>changes</u>',
            'comment': 'Write a comment and/or add a schedule',
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


def msg_enter_take_profit(lang: LANGUAGES_TYPE, tp_ratio: list[float]):
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


def msg_enter_splitting(lang: LANGUAGES_TYPE, tp_ratio: list[float], split: list[float], is_last=False):
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


def msg_enter_tool(lang: LANGUAGES_TYPE, market: MARKETS_TYPE = 'crypto', is_try=False):
    if is_try:
        texts = {
            'ru': 'Ваш инструмент (например, BTC или DOGE)\n<u>Введите</u> SOL',
            'en': 'Your tool (e.g. BTC or DOGE)\n<u>Enter</u> SOL',
            'uz': 'Sizning vositangiz (masalan BTC yoki DOGE)\n<u>Kirmoq</u> SOL',
            'tr': 'Aracın (örneğin BTC veya DOGE)\n<u>Girmek</u> SOL',
        }

        return texts[lang]
    else:
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
        current_value = f'\n<b>{msg_current_value(lang)}</b>: {current}'

    return f'👉 {texts[lang]}?' + current_value


def msg_enter_first_deposit(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Первым делом, выставите размер депозита для торговли.\n<u>Введите</u> 1000',
        'en': 'First, indicate your deposit, the sum you’re going to spend on the deal.\n<u>Enter</u> 1000',
        'uz': 'Birinchidan, sizning omonatingizni ko\'rsating, siz shartnomada o\'tkazmoqchi bo\'lgan summani.\n1000 <u>kiriting</u>',
        'tr': 'İlk olarak, depozitonuzu, anlaşmaya harcayacağınız toplamı belirtin.\n1000 <u>girin</u>',
    }

    return texts[lang]


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


def msg_enter_risk_percent(lang: LANGUAGES_TYPE):
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

    return f"""👉 {texts[lang]}

{info[lang]}{ENTER}{ENTER}{msg_risk_info(lang)}
"""


def msg_enter_first_risk_percent(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Риск на сделку (Проф. трейдеры рискуют на каждую сделку не более 1% от депозита)\n<u>Введите</u> 1%',
        'en': 'Risk per deal (Professional traders risk no more than 1% of the deposit per deal)\n<u>Enter</u> 1%',
        'uz': 'Bitim uchun xavf (professional savdogarlar bitimning 1% omonatning 1% dan ko\'pi xavf ostida)\n<u>Kirmoq</u> 1%',
        'tr': 'Anlaşma başına risk (profesyonel tüccarlar, anlaşma başına depozitonun% 1\'inden fazlası yok)\n<u>Girmek</u> 1%',
    }

    return texts[lang]


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
    if is_try:
        texts = {
            'ru': 'Цена входа в сделку (цена, по которой вы войдете в сделку согласно графику)\n<u>Введите</u> 156.04',
            'en': 'The entry price of the deal (the price at which you enter the deal according to the chart)\n<u>Enter</u> 156.04',
            'uz': 'Bitimning kirish narxi (jadvalga muvofiq bitimni kiritgan narx)\n156.04 <u>kiriting</u>',
            'tr': 'Anlaşmanın giriş fiyatı (anlaşmaya grafiğe göre girdiğiniz fiyat)\n156.04 <u>Girin</u>',
        }

        return texts[lang]
    else:
        texts = {
            'ru': 'По какой цене <b>войдёте</b> в сделку',
            'en': 'Enter the <b>opening price</b> of the deal',
            'uz': 'Savdoning ochilish narxini tanlang',
            'tr': 'İşlem açılış fiyatını girin',
        }

        return f"""👉 {texts[lang]}:"""


def msg_enter_stop_loss(lang: LANGUAGES_TYPE, is_try=False, send_stat: Calculation | None = None):
    if is_try:
        texts = {
            'ru': 'Цена стол-лосса сделки (цена, ниже или выше которой ваша сделка не будет активна, фиксация убытка)\n<u>Введите</u> 152.74',
            'en': 'The stop loss price of the deal (the price achieving which you leave the deal as not to lose your money)\n<u>Enter</u> 152.74',
            'uz': 'Bitimning stop loss narxi (pulingizni yo\'qotmaslik uchun bitimni qoldirgan narx)\n152.74 <u>kiriting</u>',
            'tr': 'Anlaşmanın stop loss fiyatı (paranızı kaybetmemek için anlaşmadan ayrıldığınız fiyat)\n152.74 <u>Girin</u>',
        }

        return texts[lang]
    else:
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
    stop = (user_settings_storage.get_user_stop(tg_id) or '').split('+')
    percent = ''

    if len(stop) == 2:
        _, percent = stop

    atr_settings = user_settings_storage.get_user_atr_settings(tg_id)
    period, count = atr_settings[1].split('+')

    texts = {
        'ru': "Выберите направление или свой стоп лосс",
        'en': "Select the direction",
        'uz': "Yo'nalishni tanlang",
        'tr': "Yönü seçin",
    }

    info = {
        'ru': "⚡️<b>Предложенные</b> цены стоп лоссов при торговле в лонг/шорт",
        'en': "⚡️<b>Suggested</b> stop loss prices when trading in long/short",
        'uz': "⚡️uzoq/qisqa savdo paytida <b>taklif</b> stop loss narxlar",
        'tr': "⚡️<b>Önerilen</b> uzun/kısa işlemlerde zararı durdur fiyatları",
    }

    atr_info = {
        'ru': f'ATR <b>{count} баров</b>',
        'en': f'ATR <b>{count} bars</b>',
        'uz': f'ATR <b>{count} bar</b>',
        'tr': f'ATR <b>{count} çubukları</b>'
    }

    avg_atr = ''
    if value is not None:
        if percent:
            percent = float(percent)
            percent = f' {get_print_float(percent, 1)}%'

        avg_atr = f'{atr_info[lang]} ({period.upper()}){percent} ~ <b>{get_print_float(value, 5)} USDT</b>'

    return f"""{avg_atr}

{info[lang]}

👇 {texts[lang]}"""


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


def msg_enter_close_price(lang: LANGUAGES_TYPE):
    if lang == 'ru':
        text = 'Введите Вашу <b>цену закрытия</b> сделки'
    elif lang == 'uz':
        text = 'Bitimni yopish narxini kiriting'
    elif lang == 'tr':
        text = 'İşlemi kapatma fiyatını girin'
    else:
        text = 'Enter <b>close price</b> of this deal'

    return f'👉 {text}'


def msg_enter_new_stop(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите цену, куда передвигаете стоп',
        'en': 'Enter the price where you move the stop',
        'uz': 'To\'xtash joyini ko\'chiradigan narxni kiriting',
        'tr': 'Durağı taşıdığınız fiyatı girin',
    }

    return f'👉 {texts[lang]}'


def msg_enter_take_price(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите цену тейка',
        'en': 'Enter the take price',
        'uz': 'Teik narxini kiriting',
        'tr': 'Alma fiyatını girin',
    }

    return f'👉 {texts[lang]}'


def msg_choose_lang(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Выберите язык',
        'en': 'Choose language',
        'uz': 'Tilni tanlang',
        'tr': 'Dil seç',
    }

    return f'🌐 {texts[lang]}'


def msg_enter_cancel_at(lang: LANGUAGES_TYPE, with_datetime=False):
    texts = {
        'ru': {
            'main': 'Выберите время, через которое сделка будет отменена, либо введите <u>количество часов</u>',
            'datetime': 'или <u>дату</u> в формате ДД.ММ ММ:ЧЧ по МСК',
        },
        'en': {
            'main': 'Select the time after which the transaction will be canceled, or enter the number of hours',
            'datetime': 'or <u>the date</u> in DD.MM MM:HH Moscow Time',
        },
        'tr': {
            'main': 'İşlemin iptal edileceği süreyi seçin veya saat sayısını girin',
            'datetime': 'veya Moskova Saat biçimindeki tarih DD.MM MM:HH',
        },
        'uz': {
            'main': 'Tranzaksiya bekor qilinadigan vaqtni tanlang yoki soat sonini kiriting',
            'datetime': 'yoki Moskva vaqt formatidagi sana DD.MM MM:HH',
        }
    }

    message = f'👉 {texts[lang]["main"]}'
    if with_datetime:
        message += f' {texts[lang]["datetime"]}'

    return message


def msg_enter_tr_stop(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Введите значение для скользящего стопа',
        'en': 'Enter a value for a sliding foot',
        'tr': 'Kayan ayak için bir değer girin',
        'uz': 'Tushunchilik oyog\'i uchun qiymatni kiriting',
    }

    info = {
        'ru': """Изменить фиксированный стоп лосс на скользящий.

<b>Выбери шаг стоп лосса</b>, а система автоматически будет изменять цену и подтягивать стоп лосс по мере движения цены инструмента.

Классический тейк профит, указанный ранее, не будет работать.

Тейк профит также будет меняться автоматически, <b>пока сделка не выбьет по стоп лоссу.</b>""",
        'en': """Change the fixed stop loss to a moving one.

<b>Select the stop loss stop</b>, and the system will automatically change the price and tighten the stop loss as the price of the instrument moves.

The classic take profit specified earlier will not work.

The take profit will also change automatically, <b>until the trade hits the stop loss.</b>""",
        'uz': """Bir harakat biriga sobit stop loss o'zgartirish.

<b>stop loss stop</b> ni tanlang va tizim avtomatik ravishda narxni o'zgartiradi va asbobning narxi harakat qilganda stop loss-ni tortadi.

Ilgari ko'rsatilgan klassik foyda ishlamaydi.

Savdo stop loss xitlar qadar take foyda ham avtomatik ravishda, <b>o'zgaradi.</b>""",
        'tr': """Sabit durma kaybını hareketli olana değiştirin.

<b>Kaybı durdur durağını seçin</b> ve sistem fiyatı otomatik olarak değiştirecek ve enstrümanın fiyatı hareket ettikçe kaybı durduracaktır.

Daha önce belirtilen klasik kar elde etmek işe yaramaz.

Alım karı da otomatik olarak değişecektir, <b>ticaret stop loss'a ulaşana kadar.</b>""",
    }

    return f'{info[lang]}\n\n👉 {texts[lang]}'


def msg_enter_auto_take(lang: LANGUAGES_TYPE, takes: list[float] = []):
    texts = {
        'ru': 'Выберите количество тейков для авто выхода',
        'en': 'Select a take for auto exit',
        'tr': 'Otomatik çıkış için Al\'ı seçin',
        'uz': 'Avtomatik chiqish uchun qabul qilishni tanlang',
    }

    takes_show = ''
    if len(takes) > 0:
        for i, el in enumerate(takes):
            takes_show += f'\n{i + 1} {"к" if lang == "ru" else "to"} 1 {" " if i + 1 >= 10 else ""}| <b>{get_print_float(el)} USDT</b>'

    return f'👉 {texts[lang]}{takes_show}'
