from models import LANGUAGES_TYPE


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
