from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from MAIN.common.utils import get_calculator_btn_link
from common.keyboard import back_txt
from common.utils import get_lang
from config_global import SITE_URL
from .filter import user_main_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, user_main_factory.new(type=type))


def kb_user_main(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'buy': 'Купить',
            'calc': 'Калькулятор',
            'account': 'Личный кабинет',
            'site': 'Войти на сайт',
        },
        'en': {
            'buy': 'Buy',
            'calc': 'Calculator',
            'account': 'Profile',
            'site': 'Go to website',
        }
    }

    # btn1 = getButton("Рекомендации", 'signals')
    btn2 = getButton(f"💰 {texts[lang]['buy']}", 'buy')
    # btn3 = getButton("Обучение", 'education')
    btn4 = getButton(f"⌨️ {texts[lang]['calc']}", 'calculator')
    btn5 = getButton(f"👨 {texts[lang]['account']}", 'account')
    btn_site = getButton(f"{texts[lang]['site']}", 'site')

    keyboard.add(btn2, btn4)
    keyboard.add(btn5, btn_site)
    return keyboard


def kb_user_calculator(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_link = get_calculator_btn_link(lang)

    keyboard.add(btn_link)
    return keyboard


def kb_site_login(user_id: int, code: str, is_reset=False):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'site': 'Войти на сайт',
        },
        'en': {
            'site': 'Go to website',
        }
    }

    btn_link = InlineKeyboardButton(
        texts[lang]['site'], url=f'{SITE_URL}/auth/tg?code={code}'
    )
    btn_reset = getButton('✅' if is_reset else '🔄', 'site_reset')
    btn_back = getButton(back_txt(lang), 'main')

    buttons = []
    if code:
        buttons.append(btn_link)
    buttons.append(btn_reset)
    buttons.append(btn_back)

    keyboard.add(*buttons)
    return keyboard
