from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt
from initialize import kb_inl_admin

from .filter import admin_statistics_factory


def getButton(text: str, type: str, filter=''):
    return InlineKeyboardButton(text, None, admin_statistics_factory.new(
        type=type, filter=filter
    ))


def kb_statistics_back():
    keyboard = InlineKeyboardMarkup(row_width=2)

    back = getButton(back_txt(), 'go_payment')

    keyboard.add(back)
    return keyboard


def kb_statistics():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Все клиенты', 'stat_pay_clients')
    btn2 = getButton('По периодам', 'stat_pay_periods')
    btn3 = getButton('По продуктам', 'stat_pay_products')

    back = getButton(back_txt(), 'go_main')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)

    keyboard.add(back)
    return keyboard


def kb_stats_periods():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Сегодня', 'stat_pay_period_choose', 'today')
    btn2 = getButton('За неделю', 'stat_pay_period_choose', 'week')
    btn3 = getButton('За месяц', 'stat_pay_period_choose', 'month')
    btn4 = getButton('За период', 'stat_pay_period_choose_start_to_end')
    btn5 = getButton('С даты по сегодня', 'stat_pay_period_choose_start_date')

    back = getButton(back_txt(), 'go_payment')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5)

    keyboard.add(back)
    return keyboard


def kb_stats_products():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Сигналы', 'stat_pay_product_choose', 'signals')
    btn2 = getButton('Калькулятор', 'stat_pay_product_choose', 'calc')
    btn3 = getButton('Сигналы+калькулятор',
                     'stat_pay_product_choose', 'calc_signals')

    back = getButton(back_txt(), 'go_payment')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    keyboard.add(back)

    return keyboard
