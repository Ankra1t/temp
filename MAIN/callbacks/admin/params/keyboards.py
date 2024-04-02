from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt
from MAIN.common.utils import get_calculator_btn_link

from .filter import admin_params_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, admin_params_factory.new(type=type))


def kb_params():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_calc = getButton('⌨️ Калькулятор', 'calculator')
    btn_texts = getButton('✏️ Изменить тексты', 'update_texts')
    btn_change = getButton('Изменить', 'change')
    btn_trial = getButton('🎁 Изменить пробный период', 'change_trial_days')

    back = getButton(back_txt(), 'go_main')

    keyboard.add(btn_calc, btn_texts)
    keyboard.add(btn_change)
    keyboard.add(btn_trial)
    keyboard.add(back)
    return keyboard


def kb_calculator():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('💲 Добавить фьючерс', 'calculator_add_future')
    btn2 = getButton('💱 Добавить валютную пару', 'calculator_add_forex')
    back = getButton(back_txt(), 'go_params')
    btn_link = get_calculator_btn_link('ru')

    keyboard.add(btn1, btn2)
    keyboard.add(btn_link)
    keyboard.add(back)
    return keyboard


def kb_params_change():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('FAQ', 'change_faq')
    btn2 = getButton('О нас', 'change_about_us')
    back = getButton(back_txt(), 'go_params')

    keyboard.add(btn1, btn2)
    keyboard.add(back)
    return keyboard


def kb_params_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    back = getButton(back_txt(), 'go_params')
    keyboard.add(back)
    return keyboard


def kb_params_choice(action: str):
    keyboard = InlineKeyboardMarkup(row_width=2)

    def getBtn(txt, type): return getButton(txt, f'{action}_choice_{type}')

    yes = getBtn('✅ Да', 'yes')
    no = getBtn('❌ Нет', 'no')

    keyboard.add(yes, no)
    return keyboard


def kb_edit_text(text_name: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    edit = getButton('✏️ Редактировать', f'edit_text+{text_name}')

    keyboard.add(edit)
    return keyboard
