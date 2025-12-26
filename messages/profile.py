from typing import Literal
from common.dt import get_datetime_now, get_str_by_datetime
from messages.common import POINT
from models import LANGUAGES_TYPE, Price, Purchase, UserInfo

from db import db


def msg_referral(lang: LANGUAGES_TYPE, ref_count: int, bot_name: str, user_db_id: int):
    texts = {
        'ru': {
            '1': f'<b>Сейчас у вас:</b> {ref_count} реферал(ов)',
            '2': '<b>Скопируйте</b> ссылку ниже и поделитесь ей со своими друзьями',
            '3': 'В будущем Вы будете получать <b>вознаграждение</b> за активность ваших рефералов',
        },
        'en': {
            '1': f'<b>Now you have:</b> {ref_count} referral(s)',
            '2': '<b>Copy</b> the link below and share it with your friends',
            '3': 'In the future, you will receive <b>reward</b> for the activity of your referrals',
        },
        'uz': {
            '1': f'<b>Hozirda sizda:</b> {ref_count} ta tavsiya(lar) bor',
            '2': 'Quyidagi havoladan nusxa oling va do\'stlaringiz bilan baham ko\'ring',
            '3': 'Kelajakda siz referallaringiz faoliyati uchun mukofot olasiz',
        },
        'tr': {
            '1': f'<b>Şu anda:</b> {ref_count} referansınız var',
            '2': 'Aşağıdaki bağlantıyı <b>kopyalayın</b> ve arkadaşlarınızla paylaşın',
            '3': 'Gelecekte, yönlendirmelerinizin etkinliği için <b>ödül</b>',
        },
    }

    return f"""{texts[lang]['1']}

{texts[lang]['2']}
{texts[lang]['3']}😉

<code>https://t.me/{bot_name}/?start={user_db_id}</code>"""


def msg_referral_list(lang: LANGUAGES_TYPE, user_db_id: int, referrals: list[UserInfo]):
    texts = {
        'ru': {
            'name': 'Ник',
            'sum': 'Всего потратил',
            'not': 'Рефералы не найдены',
        },
        'en': {
            'name': 'Nick',
            'sum': 'Spent',
            'not': 'Referrals not found',
        },
        'uz': {
            'name': 'Nik',
            'sum': 'Jami sarflangan',
            'not': 'Hech qanday havola topilmadi',
        },
        'tr': {
            'name': 'Nickname',
            'sum': 'Toplam harcama',
            'not': 'Yönlendirme bulunamadı',
        },
    }

    res = ''
    if len(referrals) != 0:
        for ref in referrals:
            name = f'@{ref.tg_username}' if ref.tg_username else '-'

            purchase = db.get_purchases_by_user(user_db_id)
            money = 0
            for el in purchase:
                money += el.sum or 0
            res += f"{POINT} {texts[lang]['name']}: {name}\n{texts[lang]['sum']}: <b>{money}</b>\n\n"
    else:
        res = f"{texts[lang]['not']} 😔\n"

    return res


def msg_site_login(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'name': 'Вход на сайт',
            'click': 'Нажмите на кнопку для перехода на сайт',
            'time': 'Ссылка действует несколько минут',
        },
        'en': {
            'name': 'Website',
            'click': 'Press the button to go to the website',
            'time': 'The link is valid for several minutes',
        },
        'uz': {
            'name': 'Saytga kiring',
            'click': 'Saytga o\'tish uchun tugmani bosing',
            'time': 'Havola bir necha daqiqa davomida amal qiladi',
        },
        'tr': {
            'name': 'Siteye giriş yap',
            'click': 'Siteye gitmek için tıklayınız',
            'time': 'Bağlantı birkaç dakika geçerlidir',
        },
    }

    return f"""<b><u>{texts[lang]['name']}</u></b>

👇 {texts[lang]['click']}
<i>{texts[lang]['time']}</i>"""


def msg_user_tariff(tariff: Price):  # TODO - переводы
    discount = ''
    if tariff.discount is not None:
        now = get_datetime_now()
        fin_date_discount = tariff.discount.findate
        if fin_date_discount > now:
            discount = f'<b>Скидка {str(round(tariff.discount.percent))}%</b>'

    return f"""
{tariff.name}
{tariff.price} {tariff.currency}
{tariff.description}
<i>действует {tariff.duration_days} дн.</i>

{discount}"""


def msg_user_account(lang: LANGUAGES_TYPE, refs: int):
    texts = {
        'ru': {
            'name': 'Личный кабинет',
            'spent': 'Всего потратили',
            'refs': 'Рефералов',
        },
        'en': {
            'name': 'Profile',
            'spent': 'Spent',
            'refs': 'Referrals',
        },
        'uz': {
            'name': 'Shaxsiy kabinet',
            'spent': 'Sarflangan',
            'refs': 'Murojaatlar',
        },
        'tr': {
            'name': 'Kişisel hesap',
            'spent': 'Harcanmış',
            'refs': 'Referans',
        },
    }

    return f"""<b><u>{texts[lang]['name']}</u></b>

{texts[lang]['refs']}: <b>{refs}</b>
"""


def msg_user_params(lang: LANGUAGES_TYPE, user: UserInfo):
    texts = {
        'ru': {
            'main': 'Параметры',
            'name': 'Никнейм',
        },
        'en': {
            'main': 'Params',
            'name': 'Nickname',
        },
        'uz': {
            'main': 'Parametrlar',
            'name': 'Nik',
        },
        'tr': {
            'main': 'Paramler',
            'name': 'Nickname',
        },
    }

    return f"""🛠 <b><u>{texts[lang]['main']}</u></b>

<b>{texts[lang]['name']}</b>: {user.nickname or '-'}"""


def msg_user_purchases(lang: LANGUAGES_TYPE, purchases: list[Purchase]):
    texts = {
        'ru': {
            'name': 'Мои покупки',
            'calc': 'Калькулятор',
            'signals': 'Рекомендации',
            'calc_signals': 'PRO',
            'date': 'Дата',
        },
        'en': {
            'name': 'My purchases',
            'calc': 'Calculator',
            'signals': 'Recommendations',
            'calc_signals': 'PRO',
            'date': 'Date',
        },
        'uz': {
            'name': 'Mening xaridlarim',
            'calc': 'Kalkulyator',
            'signals': 'Tavsiyalar',
            'calc_signals': 'PRO',
            'date': 'Sana',
        },
        'tr': {
            'name': 'Satın alımlarım',
            'calc': 'Hesap makinesi',
            'signals': 'Öneriler',
            'calc_signals': 'PRO',
            'date': 'Tarih',
        },
    }

    products = {'signals': '', 'calc': '', 'calc_signals': ''}
    for p in purchases:
        info = f'🛍 "<b>{p.price_name}</b>" <u>{p.sum}</u> {p.currency}'
        info += f'\n{texts[lang]["date"]} {get_str_by_datetime(p.payment_date or get_datetime_now())}\n'

        type_p = p.type_product or 'calc'

        prev = products[type_p]
        if prev != '':
            products[type_p] += '\n'
        products[type_p] += info

    result = f'<b><u>{texts[lang]["name"]}</u></b>\n'

    if len(purchases) == 0:
        result += '\n Нет покупок'
        return result

    if products['calc'] != '':
        result += f'\n{POINT} <b>{texts[lang]["calc"]}</b>\n'
        result += products['calc']

    if products['signals'] != '':
        result += f'\n{POINT} <b>{texts[lang]["signals"]}</b>\n'
        result += products['signals']

    if products['calc_signals'] != '':
        result += f'\n{POINT} <b>{texts[lang]["calc_signals"]}</b>\n'
        result += products['calc_signals']

    return result


def msg_enter_nickname(lang: LANGUAGES_TYPE, error: Literal['min', 'max', 'taken', 'default'] | None = None):
    texts = {
        'ru': {
            'err_min': 'Минимальная длина 4 символа',
            'err_max': 'Максимальная длина 16 символа',
            'err': 'Ошибка',
            'taken': 'Имя уже занято',
            'main': 'Введите никнейм',
            'dop': 'В никнейме могут быть только символы латинского алфавита и цифры'
        },
        'en': {
            'err_min': 'Min length is 4 characters',
            'err_max': 'Max length is 16 characters',
            'err': 'Error',
            'taken': 'The nickname is already in use',
            'main': 'Enter a nickname',
            'dop': 'The nickname can only contain Latin letters and numbers'
        },
        'uz': {
            'err_min': 'Minimal uzunlik 4 ta belgi',
            'err_max': 'Maksimal uzunlik 16 ta belgi',
            'err': 'Xato',
            'taken': 'Ism allaqachon olingan',
            'main': 'Taxallusingizni kiriting',
            'dop': 'Taxallus faqat lotin alifbosi va belgilarini o\'z ichiga olishi mumkin'
        },
        'tr': {
            'err_min': 'Minimum uzunluk 4 karakter',
            'err_max': 'Maksimum uzunluk 16 karakter',
            'err': 'Hata',
            'taken': 'İsim alınmış',
            'main': 'Takma adınızı giriniz',
            'dop': 'Takma ad yalnızca Latin karakterleri ve sayıları içerebilir'
        },
    }

    error_mes = ''
    if error == 'min':
        error_mes = texts[lang]['err_min']
    elif error == 'max':
        error_mes = texts[lang]['err_max']
    elif error == 'default':
        error_mes = texts[lang]['err']
    elif error == 'taken':
        error_mes = texts[lang]['taken']

    if error_mes != '':
        error_mes = f'❗️ {error_mes}\n\n'

    return error_mes + f"""<i>{texts[lang]['dop']}</i>
✍ {texts[lang]['main']}"""
