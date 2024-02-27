from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from initialize import kb_inl_admin
from MAIN.common.utils import get_calculator_btn_link

from .filter import admin_params_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, admin_params_factory.new(type=type))


def kb_params():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('⌨️ Калькулятор', 'calculator')
    btn2 = getButton('✏️ Изменить тексты', 'update_texts')
    btn4 = getButton('Изменить', 'change')
    btn5 = getButton('🎁 Изменить пробный период', 'change_trial_days')

    keyboard.add(btn1, btn2)
    keyboard.add(btn4)
    # keyboard.add(btn3, btn4)
    keyboard.add(btn5)
    keyboard.add(kb_inl_admin.go_main_btn)
    return keyboard


def kb_calculator():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('💲 Добавить фьючерс', 'calculator_add_future')
    btn2 = getButton('💱 Добавить валютную пару', 'calculator_add_forex')
    btn_link = get_calculator_btn_link()

    keyboard.add(btn1, btn2)
    keyboard.add(btn_link)
    keyboard.add(kb_inl_admin.go_params_btn, kb_inl_admin.go_main_btn)
    return keyboard


def kb_params_change():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('FAQ', 'change_faq')
    btn2 = getButton('О нас', 'change_about_us')

    keyboard.add(btn1, btn2)
    keyboard.add(kb_inl_admin.go_params_btn, kb_inl_admin.go_main_btn)
    return keyboard


def kb_params_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(kb_inl_admin.go_params_btn, kb_inl_admin.go_main_btn)
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