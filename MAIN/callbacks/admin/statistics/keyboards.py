from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from initialize import kb_inl_admin
from MAIN.common.utils import get_calculator_btn_link

from .filter import admin_statistics_factory


def getButton(text: str, type: str, filter=''):
    return InlineKeyboardButton(text, None, admin_statistics_factory.new(
        type=type, filter=filter
    ))

def kb_statistics_back():
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(kb_inl_admin.go_statistics_btn, kb_inl_admin.go_main_btn)
    return keyboard

def kb_statistics():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('По клиентам', 'stat_pay_clients')
    btn2 = getButton('По периодам', 'stat_pay_periods')
    btn3 = getButton('По продуктам', 'stat_pay_products')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)

    keyboard.add(kb_inl_admin.go_main_btn)
    return keyboard

def kb_stats_periods():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Сегодня', 'stat_pay_period_choose', 'today')
    btn2 = getButton('За неделю', 'stat_pay_period_choose', 'week')
    btn3 = getButton('За месяц', 'stat_pay_period_choose', 'month' )
    btn4 = getButton('За период', 'stat_pay_period_choose', 'start_to_end' )
    btn5 = getButton('С даты по сегодня', 'stat_pay_period_choose', 'start_date' )

    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5)

    keyboard.add(kb_inl_admin.go_statistics_btn, kb_inl_admin.go_main_btn)
    return keyboard



