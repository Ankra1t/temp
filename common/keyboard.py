
# TODO - перенос в keyboards.common

from models import LANGUAGES_TYPE


def back_txt(lang: LANGUAGES_TYPE = 'ru'):
    txt: dict[LANGUAGES_TYPE, str] = {
        'ru': 'Назад',
        'en': 'Back',
        'uz': 'Orqaga',
        'tr': 'Geri',
    }

    return f'🔙 {txt[lang]}'


def reset_txt(lang: LANGUAGES_TYPE = 'ru'):
    txt: dict[LANGUAGES_TYPE, str] = {
        'ru': 'Сбросить',
        'en': 'Reset',
        'uz': 'Qayta o\'rnatmoq',
        'tr': 'Sıfırlamak',
    }

    return f'{txt[lang]}'


def cancel_txt(lang: LANGUAGES_TYPE = 'ru'):
    txt: dict[LANGUAGES_TYPE, str] = {
        'ru': 'Отмена',
        'en': 'Cancel',
        'uz': 'Bekor qilish',
        'tr': 'İptal et',
    }

    return f'⚠️ {txt[lang]}'
