from typing import Literal
from common.utils import get_print_float
from messages.common import POINT, msg_atr_bars, transl_market, transl_tr_style, transl_tr_type, msg_current_value
from models import LANGUAGES_TYPE, AdvancedSettings

# TODO - delete db from messages files
from service import user_settings_storage, UserSettings


def msg_settings(lang: LANGUAGES_TYPE, u_base: UserSettings, is_risk_update=False):
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


def msg_deposit(lang: LANGUAGES_TYPE, u_base: UserSettings | None, stop: str | None):
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
{info_upd[lang]}"""


def msg_settings_change_base(lang: LANGUAGES_TYPE):
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


def msg_settings_change_market(lang: LANGUAGES_TYPE):
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


def msg_dop_settings(lang: LANGUAGES_TYPE, output: Literal['text', 'photo'], risk_upd: bool):
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
{msg_current_value(lang)}: <b>{texts[lang][output]}</b>

{texts[lang]['risk']}
{msg_current_value(lang)}: <b>{texts[lang]['on' if risk_upd else 'off']}</b>"""


def msg_summary_profit_settings(lang: LANGUAGES_TYPE, user_db_id: int):
    u_base = user_settings_storage.get_or_create(user_db_id)
    tp_ratio = u_base.tp_ratio if (u_base is not None) else []
    split_values = u_base.split_values if (u_base is not None) else None

    texts = {
        'ru': {
            'name': 'Настройки',
            'info': 'Деление тейк-профита позволяет выходить из сделки частями, заранее зная цену, объем для фиксации',
            'subname': 'Деление профита',
            'take_profit': 'Ваш тейк-профит',
            'split': 'Разделение',
            'on': 'включено',
            'off': 'выключено',
        },
        'en': {
            'name': 'Settings',
            'info': 'The division of the take profit allows you to leave the transaction in parts, knowing in advance the price, the volume for fixation',
            'subname': 'Profit division',
            'take_profit': 'Your take profit',
            'split': 'Splitting',
            'on': 'turned on',
            'off': 'turned off',
        },
        'uz': {
            'name': 'Sozlamalari',
            'info': "Formni olishning bo'linishi sizga bitimni qismlarga, fiksatov uchun hajmini bilish, narxni bilish, narxni bilish, narxni ajratish va",
            'subname': 'Daromad taqsimoti',
            'take_profit': 'Sizning daromadingiz',
            'split': 'Ajratish',
            'on': 'Kiritilgan',
            'off': 'o\'chirilgan',
        },
        'tr': {
            'name': 'Ayarlar',
            'info': 'Kâr Alma Bölümü, fiyatı önceden bilerek işlemi parçalar halinde bırakmanıza izin verir, tespit hacmi',
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

    return f"""⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>

{texts[lang]['info']}

{texts[lang]["split"]}: <b>{texts[lang][on_off]}</b>
{info_result}"""


def msg_change_style_settings(lang: LANGUAGES_TYPE, style: str, style_update_on: bool):
    info = {
        'ru': """Трейдеры имеют разные <b>стили торговли</b>, выбери самый частый и подходящий, а мы будем учитывать это в статистике

Во время расчетов, также, можно <b>изменять</b> на другой стиль, некоторые трейдеры могут отторговывать сразу несколько стратегий (для этого выберите "вкл/выкл изменения)""",
        'en': """Traders have different trading styles. Choose the most frequent and appropriate one, and we will consider it in the statistics

During calculations, you can also change your trading style. Some traders can practice several strategies at once (select "on/off the change" for this).""",
        'uz': """Savdogarlar turli xil savdo uslublariga ega.Eng tez-tez va mosni tanlang va biz buni statistikada ko'rib chiqamiz

Hisob-kitoblar paytida siz savdo uslubingizni ham o'zgartirishingiz mumkin.Ba'zi savdogarlar bir vaqtning o'zida bir nechta strategiyani mashq qilishlari mumkin ("O'zgarishni yoqish / o'chirish" ni tanlang).""",
        'tr': """Tüccarların farklı ticaret stilleri vardır.En sık ve uygun olanı seçin ve bunu istatistiklerde ele alacağız

Hesaplamalar sırasında ticaret stilinizi de değiştirebilirsiniz.Bazı tüccarlar aynı anda çeşitli stratejiler uygulayabilirler (bunun için "Aç/Kapalı Değişiklik" i seçin).""",
    }

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

{info[lang]}

{POINT} {msg_current_value(lang)}: <b>{transl_tr_style(style, lang) or '-'}</b>
{POINT} {texts[lang]['update']}: <b>{texts[lang]['on'] if style_update_on else texts[lang]['off']}</b>
"""


def msg_exchange(lang: LANGUAGES_TYPE, exchange: tuple[str, float] | None = None):
    info = {
        'ru': '<b>Учитывайте</b> комиссии с бирж при расчете сделок, заранее понимая, какая сумма с каждой сделки будет вычитаться и точнее управляйте риск-менеджментом',
        'en': '<b>Consider</b> exchange fees when calculating trades, aware in advance which amount will be deducted from each trade, and perform risk management more carefully.',
        'uz': "Bitimlarni hisoblashda operatsiyalarni hisoblashda, har bir operatsiyaning qancha miqdorini pasaytirish va xavflarni boshqarishning qaysi miqdorini aniqlab olishini va aniqroq nazoratni tushunishni ko'rib chiqing",
        'tr': 'İşlemleri hesaplarken, her işlemden hangi miktarın düşüleceğini anlama ve risk yönetimini daha doğru bir şekilde kontrol ederken borsalardan gelen komisyonları düşünün'
    }

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

    return f"""<b><u>{texts[lang]['main']}</u></b>

{info[lang]}{current}"""


def msg_maker_or_taker(lang: LANGUAGES_TYPE, maker_fee: float, taker_fee: float):
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


def msg_enter_exchange(lang: LANGUAGES_TYPE):
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


def msg_enter_exchange_not_found(lang: LANGUAGES_TYPE, is_diff=False):
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


def msg_choose_exchange_level(lang: LANGUAGES_TYPE, fees: list[tuple[str, float, float]]):
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


def msg_stop_page(
    lang: LANGUAGES_TYPE,
    atr_settings: tuple[bool, str],
    stop_type: str | None,
    is_update_deposit=False,
):
    texts = {
        'ru': {
            'main': "Выберите вид риска",
            'value': "Текущий",

            'fd': "от депозита",
            'default': "Обычный",

            'auto': 'автоматический',
            'self': 'ручной',

            'atr_auto': "Расчёт",
            'last': "последние",
            'pieces': "последние",
        },
        'en': {
            'main': "Choose the type of risk",
            'value': "Current",

            'fd': "from the deposit",
            'default': "Default",

            'auto': 'automatic',
            'self': 'manual',

            'atr_auto': "Calculation",
            'last': "last",
        },
        'uz': {
            'main': "Xavf turini tanlang",
            'value': "Hozirgi",

            'fd': "Omonatdan",
            'default': "Oddiy",

            'auto': 'avtomatik',
            'self': 'qo\'llanma',

            'atr_auto': "Hisoblash",
            'last': "ikkinchisi",
        },
        'tr': {
            'main': "Bir tür risk seçin",
            'value': "Akım",

            'fd': "depozitodan",
            'default': "Sıradan",

            'auto': 'otomatik',
            'self': 'manuel',

            'atr_auto': "Hesaplama",
            'last': "İkincisi",
        },
    }

    atr_info = ''
    if is_update_deposit:
        stop_show = texts[lang]['fd']
    elif stop_type is None:
        stop_show = '-'
    elif stop_type == 'default':
        stop_show = texts[lang]['default']
    elif stop_type == 'atr':
        stop_show = 'ATR'

        atr_info = f'{texts[lang]["atr_auto"]}: <b>{texts[lang]["auto" if atr_settings[0] else "self"]}</b>'
        atr_info += f'\n({msg_atr_bars(lang, atr_settings[1])})'
    else:
        _, percent = stop_type.split('+')
        stop_show = f'{percent}% of ATR'

    return f"""<b><u>{texts[lang]['main']}</u></b>

{texts[lang]['value']}: <b>{stop_show}</b>
""" + atr_info


def msg_atr_settings(lang: LANGUAGES_TYPE, atr_settings: tuple[bool, str]):
    texts = {
        'ru': {
            'main': 'Настройка ATR',
            'calc': 'Расчёт',
            'auto': 'автоматический',
            'self': 'ручой',
            'auto_atr': 'Бары',
            'avg': 'среднее'
        },
        'en': {
            'main': 'ATR setup',
            'calc': 'Calculation',
            'auto': 'automatic',
            'self': 'manual',
            'auto_atr': 'Bars',
            'avg': 'average'
        },
        'uz': {
            'main': 'ATR sozlamalari',
            'calc': 'Hisoblash',
            'auto': 'avtomatik',
            'self': 'qo\'llanma',
            'auto_atr': 'Ayiq',
            'avg': 'o\'rtacha'
        },
        'tr': {
            'main': 'ATR kurulumu',
            'calc': 'Hesaplama',
            'auto': 'otomatik',
            'self': 'manuel',
            'auto_atr': 'Ayı',
            'avg': 'ortalama'
        },
    }

    bars = ''
    if atr_settings[1] != '':
        period, count = atr_settings[1].split('+')
        bars = f'{texts[lang]["auto_atr"]}: {period} ({texts[lang]["avg"]} {count})'

    return f"""<u><b>{texts[lang]["main"]}</b></u>

{texts[lang]['calc']}: {texts[lang]['auto'] if atr_settings[0] else texts[lang]['self']}
""" + bars


def msg_confirm_reset(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Вы действительно хотите <b>сбросить</b> все настройки',
        'en': 'Do you really want to  <b>return to default</b> settings',
        'uz': 'Haqiqatan ham barcha sozlamalarni tiklamoqchimisiz',
        'tr': 'Tüm ayarları <b>sıfırlamak</b> istediğinizden emin misiniz',
    }

    return f'⚠️ {texts[lang]}?'


def msg_active_settings(
    lang: LANGUAGES_TYPE, data: AdvancedSettings | None
):
    texts = {
        'ru': {
            'main': 'Настройка активных сделок',
            'trailing': 'Скользящий стоп',
            'cancelAt': 'Отмена через (часов)',
            'take': 'Тейк',
        },
        'en': {
            'main': 'Setting of active trades',
            'trailing': 'Tr. stop',
            'cancelAt': 'Cancellation after (hours)',
            'take': 'Take',
        },
        'uz': {
            'main': 'Faol savdolarni sozlash',
            'trailing': 'Slip stop',
            'cancelAt': 'Bekor keyin (soat)',
            'take': 'Take',
        },
        'tr': {
            'main': 'Aktif işlemlerin ayarlanması',
            'trailing': 'Iptal etmek',
            'cancelAt': '(Saat) sonra iptal',
            'take': 'Take',
        },
    }

    take = '-'
    if data and data.trailingStop:
        take = f'скользящий стоп каждые {get_print_float(data.trailingStop, 1)} тейка'
    elif data and data.autoTake:
        take = f'выход при {get_print_float(data.autoTake)} тейках'

    return f"""<b>{texts[lang]['main']}</b>
{texts[lang]['take']}: {take}
{texts[lang]['cancelAt']}: {get_print_float(data.cancelMinutes / 60, 1) if data and data.cancelMinutes else '-'}"""
