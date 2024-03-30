from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from MAIN.common.utils import get_calculator_btn_link
from common.keyboard import back_txt
from config_global import SITE_URL
from .filter import user_main_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, user_main_factory.new(type=type))


def kb_user_main():
    keyboard = InlineKeyboardMarkup(row_width=2)

    # btn1 = getButton("Рекомендации", 'signals')
    btn2 = getButton("💰 Купить", 'buy')
    # btn3 = getButton("Обучение", 'education')
    btn4 = getButton("⌨️ Калькулятор", 'calculator')
    btn5 = getButton("👨 Личный кабинет", 'account')
    btn_site = getButton("Войти на сайт", 'site')

    keyboard.add(btn4, btn2)
    keyboard.add(btn5, btn_site)
    return keyboard


def kb_user_calculator():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_link = get_calculator_btn_link()

    keyboard.add(btn_link)
    return keyboard


def kb_site_login(code: str, is_reset=False):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_link = InlineKeyboardButton(
        'Войти на сайт', url=f'{SITE_URL}/auth/tg?code={code}'
    )
    btn_reset = getButton('✅' if is_reset else '🔄', 'site_reset')
    btn_back = getButton(back_txt('ru'), 'main')

    buttons = []
    if code:
        buttons.append(btn_link)
    buttons.append(btn_reset)
    buttons.append(btn_back)

    keyboard.add(*buttons)
    return keyboard
