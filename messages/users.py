from models import LANGUAGES_TYPE


def end_trial_subscribe_msg(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'Ваша пробная подписка закончилась. Вы можете оформить платную подписку.',
        'en': 'Your trial subscription has expired. You can sign up for a paid subscription.',
        'uz': 'Sinov obunangiz tugadi. Siz pullik obuna uchun ro\'yxatdan o\'tishingiz mumkin.',
        'tr': 'Maalesef deneme aboneliğinizin süresi doldu. Ücretli bir abonelik satın alabilir ve hizmeti kullanmaya devam edebilirsiniz.',
    }

    return f'❗️ {text[lang]}'


def end_paid_subscribe_msg(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'Ваша платная подписка закончилась. Пожалуйста, продлите подписку, чтобы снова пользоваться сервисом.',
        'en': 'Your paid subscription has expired. Please renew your subscription to have access to the service again.',
        'uz': 'Pulli obuna muddati tugadi, xizmatlardan qayta foydalanish uchun obunangizni yangilang.',
        'tr': 'Hizmetlerimizden yararlanmak istiyorsanız lütfen aboneliğinizi yenileyin.',
    }

    return f'❗️ {text[lang]}'


def gift_subscribe_msg(lang: LANGUAGES_TYPE, end_date: str):
    texts = {
        'ru': 'Поздравляем, админ подарил вам платную подписку до',
        'en': 'Congratulations, admin gave you a paid subscription to',
        'uz': 'Tabriklar, admin sizga pullik obuna berdi',
        'tr': 'Tebrikler, Yönetici size ücretli bir abonelik verdi',
    }

    return f"""{texts[lang]} <b>{end_date}</b>"""


def gift_trial_subscribe_msg(lang: LANGUAGES_TYPE, end_date: str):
    texts = {
        'ru': 'Вам выдан бесплатный период до',
        'en': 'You have been issued a free period before',
        'uz': 'Siz ilgari bepul vaqt berildi',
        'tr': 'Daha önce boş bir dönem verildi',
    }

    return f"""{texts[lang]} <b>{end_date}</b>"""


def paid_subscribe_msg(lang: LANGUAGES_TYPE, end_date: str, tariff_name: str):
    texts = {
        'ru': f'Благодарим за оплату подписки, <b>"{tariff_name}"</b> будет действовать <b>до {end_date}</b>',
        'en': f'Thank you for completing your subscription payment, <b>"{tariff_name}"</b> will be valid <b>until {end_date}</b>',
        'uz': f'Obuna uchun to\'laganingiz uchun rahmat, <b>"{tariff_name}"</b> {end_date} yilgacha amal qiladi',
        'tr': f'Abonelik için ödeme yaptığınız için teşekkür ederiz, <b>"{tariff_name}"</b> <b>{end_date}</b> tarihine kadar geçerli olacaktır.',
    }

    return texts[lang]


def paid_subscribe_refer_msg(lang: LANGUAGES_TYPE, user: str, sum: str):
    texts = {
        'ru': f'Ваш реферал {user} оплатил подписку на {sum}',
        'en': f'Your referral {user} paid for subscription by {sum}',
        'uz': f'Sizning tavsiyanomangiz {user} {sum} obunani to\'ladi',
        'tr': f'Tavsiyeniz {user} {sum} tutarında abonelik ödemesi yaptı',
    }

    return texts[lang]


def welcome_msg():
    return f"""
<b>«Для Людей»</b> - проект, в котором собраны обычные, простые, добрые люди. 

<b>Задача</b> проста - научиться вместе делать деньги. 
<b>Помочь</b> друг другу быть полезными. 

Теперь <b>мы вместе.</b> 
Добро пожаловать!

На <b>бесплатной</b> основе в этом чате Вы будете получать ежедневно рекомендации и информацию по торговле. 
"""


def welcome_trial_subscribe_msg(days: int = 2):
    return f"""
Поздравляем, за вашу регистрацию в боте вы получаете {str(days)} дн бесплатных рекомендаций! Пользуйтесь, и если понравиться можете
купить подписку на месяц
"""


def msg_start(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'name': 'Меню',
            'action': 'Выберите действие'
        },
        'en': {
            'name': 'Menu',
            'action': 'Choose an action'
        },
        'uz': {
            'name': 'Menyu ',
            'action': 'Harakatni tanlang'
        },
        'tr': {
            'name': 'Menü',
            'action': 'Bir Eylem Seçin'
        },
    }

    return f"""⚡️ <b><u>{texts[lang]['name']}</u></b>"""
# {texts[lang]['action']}


def msg_choose_tariff_type(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'Какой продукт вас интересует?',
        'en': 'Which product interests you?',
        'uz': 'Qaysi mahsulot sizni qiziqtiradi?',
        'tr': 'Hangi ürünle ilgileniyorsunuz?',
    }

    return text[lang]


def msg_loading_invoice(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Подготавливаем для вас возможные способы оплаты',
        'en': 'Prepare possible payment methods for you',
        'uz': 'Biz siz uchun mumkin bo\'lgan to\'lov usullarini tayyorlamoqdamiz',
        'tr': 'Sizin için ödeme seçeneklerini hazırlamaktayız',
    }

    return f'⏳ {texts[lang]}...'


def msg_is_subscribed(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'У вас уже есть подписка. Мы сообщим вам о ее завершении для следующей покупки.',
        'en': 'You already have a subscription. We will inform you about its completion before the next period.',
        'uz': 'Sizda allaqachon obuna bor, keyingi xaridingiz tugashi haqida sizga xabar beramiz.',
        'tr': 'Zaten aboneliğiniz var. Sona erdiğinde tekrar abone olmanız için sizi bilgilendireceğiz.',
    }

    return f'✅ {text[lang]}'


def msg_bill(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            '1': 'Нажмите на кнопку и оплатите тариф',
            '2': 'После подтверждения оплаты вам придет сообщение'
        },
        'en': {
            '1': 'Click on the button and pay the subscription',
            '2': 'After confirming the payment, you will receive a message'
        },
        'uz': {
            '1': 'Tugmani bosing va tarifni to\'lang',
            '2': 'to\'lov tasdiqlangandan keyin sizga xabar keladi'
        },
        'tr': {
            '1': 'Ödeme yapmak için tıklayınız',
            '2': 'Ödeme onaylandıktan sonra bir mesaj alacaksınız'
        },
    }

    return f"""{texts[lang]["1"]} 👇
{texts[lang]["2"]}"""


def msg_no_tariffs(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Тарифов нет',
        'en': 'There are no subscribtions available',
        'uz': 'Tariflar yo\'q',
        'tr': 'Tarife yok',
    }

    return texts[lang]
