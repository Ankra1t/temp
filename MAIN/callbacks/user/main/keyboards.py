from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from MAIN.common.utils import get_calculator_btn_link
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

    keyboard.add(btn4, btn2)
    keyboard.add(btn5)
    return keyboard


def kb_user_calculator():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_link = get_calculator_btn_link()

    keyboard.add(btn_link)
    return keyboard
