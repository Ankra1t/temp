from common.utils import get_lang


def end_trial_subscribe_msg(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'Ваша пробная подписка закончилась. Вы можете оформить платную подписку.',
        'en': 'Your trial subscription has ended. You can sign up for a paid subscription.',
    }

    return f'❗️ {text[lang]}'


def end_paid_subscribe_msg(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'Ваша платная подписка закончилась. Пожалуйста, продлите подписку, чтобы снова пользоваться сервисом.',
        'en': 'Your paid subscription has ended. Please renew your subscription to receive recommendations again.',
    }

    return f'❗️ {text[lang]}'


def gift_subscribe_msg(user_id: int, end_date: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Поздравляем, админ подарил вам платную подписку до',
        'en': 'Congratulations, admin gave you a paid subscription to',
    }

    return f"""{texts[lang]} <b>{end_date}</b>"""


def gift_trial_subscribe_msg(user_id: int, end_date: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Вам выдан бесплатный период до',
        'en': 'You have been issued a free period before',
    }

    return f"""{texts[lang]} <b>{end_date}</b>"""


def paid_subscribe_msg(end_date, tariff_name):
    return f"""
Благодарим за оплату подписки, <b>"{tariff_name}"</b> будет действовать <b>до {end_date}</b>
"""


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


def msg_start(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'Доброго времени. Выберите действие',
        'en': 'Good time. Choose an action'
    }

    return text[lang]


def msg_choose_tariff_type(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'Какой продукт вас интересует?',
        'en': 'Which product interests you?',
    }

    return text[lang]


def msg_loading_invoice(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Подготавливаем для вас возможные способы оплаты',
        'en': 'Prepare possible payment methods for you',
    }

    return f'⏳ {texts[lang]}...'


def msg_is_subscribed(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'У вас уже есть подписка. Мы сообщим вам о ее завершении для следующей покупки.',
        'en': 'You already have a subscription. We will inform you about its completion for the next purchase.'
    }

    return f'✅ {text[lang]}'


def msg_cryptopay(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>',
        'en': 'After the transition to Cryptobot, click <b>\"START\"</b> and <b>pay the bill</b>'
    }

    return f'❗️ {texts[lang]}'


def msg_yookassa(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'Нажмите на кнопку и оплатите тариф',
            '2': 'После подтверждения оплаты вам придет сообщение'
        },
        'en': {
            '1': 'Click on the button and pay the tariff',
            '2': 'After confirming the payment, you will receive a message'
        }
    }

    return f"""{texts[lang]["1"]} 👇
{texts[lang]["2"]}"""


def msg_pays(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Выберите удобный способ оплаты (регистрация не требуется)',
        'en': 'Select a convenient payment method (registration is not required)',
    }

    return f'❗️ {texts[lang]}'


def msg_no_tariffs(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Тарифов нет',
        'en': 'There are no tariffs',
    }

    return texts[lang]
