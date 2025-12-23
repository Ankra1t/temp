from datetime import datetime
from messages.common import msg_freeze_info, transl_market
from models import LANGUAGES_TYPE, MARKETS_TYPE
from common.dt import get_str_by_datetime


def msg_main(lang: LANGUAGES_TYPE, is_rus=False):
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
2. <b>{texts[lang]["2"]}</b>"""


def msg_no_uses(lang: LANGUAGES_TYPE):
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

    return f"""❗️ {text[lang]["1"]}
{text[lang]["2"]}"""


def msg_frozen(lang: LANGUAGES_TYPE, datetime: str):
    text = {
        'ru': 'Калькулятор заморожен до',
        'en': 'The calculator is frozen until',
        'uz': 'Kalkulyator qotib qolgan',
        'tr': 'Hesap makinesi tarihine kadar donduruldu',
    }

    return f'❄️ {text[lang]} <b>{datetime}</b>'


def msg_main_freeze(lang: LANGUAGES_TYPE, freeze_dt: datetime):
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

{msg_frozen(lang, get_str_by_datetime(freeze_dt))}"""


def msg_welcome(lang: LANGUAGES_TYPE):
    if lang == 'ru':
        return f"""Как работает калькулятор:

<b>Мой баланс</b>: 10 000 USDT

<b>Инструмент</b>: Биткоин
<b>Цена</b>: 62000 USDT

Сколько монет нужно купить на <b>10 000</b> USDT?"""
    elif lang == 'uz':
        return f"""Kalkulyator qanday ishlaydi:

<b>Mening balansim</b>: 10 000 USDT

<b>Asbob</b>: Bitcoin
<b>Narx</b>: 62000 USDT

Siz sotib olishingiz kerak bo'lgan juda ko'p tanga <b>10 000</b> USDT?"""
    elif lang == 'tr':
        return """Hesap Makinesi Nasıl Çalışır?:

<b>Benim dengem</b>: 10 000 USDT

<b>Enstrüman</b>: Bitcoin
<b>Fiyat</b>: 62000 USDT

Kaç para satın almanız gerekiyor <b>10 000</b> USDT?"""
    else:
        return """How the calculator works:

<b>My balance</b>: 10 000 USDT

<b>Instrument</b>: Bitcoin
<b>Price</b>: 62000 USDT

How many coins you need to buy for <b>10 000</b> USDT?"""


def msg_after_first_settings(
    lang: LANGUAGES_TYPE,
    dep: float,
    currency: str,
    market: MARKETS_TYPE,
    risk: float
):
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

    return f"""<b>{texts[lang]['market']}</b>: {transl_market(market, lang)}
<b>{texts[lang]['dep']}</b>: {dep} {currency}
<b>{texts[lang]['risk']}</b>: {risk}%"""


def msg_success_base_set(lang: LANGUAGES_TYPE):
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

    return f"""✅ {texts[lang]["1"]}!
{texts[lang]["2"]} ⚙️"""


def msg_support(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Чтобы связаться с тех. поддержкой, нажмите на кнопку ниже',
        'en': 'To contact the customer support, click on the button below',
        'uz': 'Texnik yordam bilan bog\'lanish uchun quyidagi tugmani bosing',
        'tr': 'Teknik destek ile iletişime geçmek için aşağıdaki butona tıklayın',
    }

    return f'{texts[lang]}👇'


def msg_freeze_calc(lang: LANGUAGES_TYPE, risk_value: str):
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

{texts[lang]['end']}."""
