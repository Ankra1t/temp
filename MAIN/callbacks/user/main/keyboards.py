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
            'support': 'Тех. поддержка',
            'site': 'Войти на сайт',
        },
        'en': {
            'buy': 'Buy',
            'calc': 'Calculator',
            'account': 'Profile',
            'support': 'Support',
            'site': 'Go to website',
        }
    }

    # btn1 = getButton("Рекомендации", 'signals')
    # btn_buy = getButton(f"💰 {texts[lang]['buy']}", 'buy')
    btn_support = getButton(f"{texts[lang]['support']}", 'support')
    # btn3 = getButton("Обучение", 'education')
    btn_calc = getButton(f"⌨️ {texts[lang]['calc']}", 'calculator')
    btn_account = getButton(f"👨 {texts[lang]['account']}", 'account')
    # btn_site = getButton(f"{texts[lang]['site']}", 'site')

    keyboard.add(btn_calc)
    keyboard.add(btn_support, btn_account)
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

def kb_support(user_id: int, link: str):
    link = link.replace('@', '')
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'operator': 'Перейти к оператору',
        },
        'en': {
            'operator': 'Go to the operator',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_link = InlineKeyboardButton(
        texts[lang]['operator'], f'https://t.me/{link}'
    )
    btn_back = getButton(back_txt(lang), 'main')

    keyboard.add(btn_link, btn_back)
    return keyboard