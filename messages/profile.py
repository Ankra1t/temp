from typing import Literal
from models import LANGUAGES_TYPE


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


def msg_user_account(lang: LANGUAGES_TYPE, refs: int):
    texts = {
        'ru': {
            'name': 'Личный кабинет',
            'refs': 'Рефералов',
        },
        'en': {
            'name': 'Profile',
            'refs': 'Referrals',
        },
        'uz': {
            'name': 'Shaxsiy kabinet',
            'refs': 'Murojaatlar',
        },
        'tr': {
            'name': 'Kişisel hesap',
            'refs': 'Referans',
        },
    }

    return f"""<b><u>{texts[lang]['name']}</u></b>

{texts[lang]['refs']}: <b>{refs}</b>
"""


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
