from db import LANGUAGES_TYPE


def back_txt(lang: LANGUAGES_TYPE = 'ru'):
    txt: dict[LANGUAGES_TYPE, str] = {
        'ru': 'Назад',
        'en': 'Back'
    }

    return f'🔙 {txt[lang]}'


def cancel_txt(lang: LANGUAGES_TYPE = 'ru'):
    txt: dict[LANGUAGES_TYPE, str] = {
        'ru': 'Отмена',
        'en': 'Cancel'
    }

    return f'⚠️ {txt[lang]}'
