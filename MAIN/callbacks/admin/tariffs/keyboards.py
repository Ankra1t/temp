from typing import Literal
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt

from .filter import admin_tariffs_factory


def getButton(text: str, type: str, page=0, id=-1):
    return InlineKeyboardButton(
        text, None,
        admin_tariffs_factory.new(type=type, page=page, id=id)
    )


def kb_admin_tariffs():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_list = getButton('Список', 'list')
    btn_add = getButton('Добавить', 'add')
    btn_back = getButton(back_txt(), 'go_main')

    keyboard.add(btn_list, btn_add)
    keyboard.add(btn_back)
    return keyboard


def kb_admin_tariffs_list(count: int, page: int, id: int, is_active: bool, is_discount: bool):
    keyboard = InlineKeyboardMarkup(row_width=3)

    next = page + 1
    prev = page - 1

    if page == 0:
        prev = count - 1
    elif page == count - 1:
        next = 0

    counter = getButton(f'{page + 1}/{count}', '')
    btn_prev = getButton('⬅️', 'list', prev)
    btn_next = getButton('➡️', 'list', next)
    btn_back = getButton(back_txt(), 'go_tariffs_del')

    btn_edit = getButton('✏️ Редактировать', 'edit', page, id)
    btn_delete = getButton('🗑 Удалить', 'delete', page, id)

    btn_on_off = getButton(
        '🔴 Отключить' if is_active else '🟢 Включить',
        'on_off', page, id
    )

    if is_discount:
        btn_discount = getButton(
            '🏷 Убрать скидку', 'discount_remove', page, id)
    else:
        btn_discount = getButton('🏷 Добавить скидку', 'discount', page, id)

    keyboard.add(btn_prev, counter, btn_next)
    keyboard.add(btn_edit, btn_on_off)
    keyboard.add(btn_discount, btn_delete)
    keyboard.add(btn_back)
    return keyboard


def kb_admin_tariff_add_type():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_calc = getButton('Калькулятор', 'add+calc')
    btn_signals = getButton('Рекомендации', 'add+signals')
    btn_calc_signals = getButton('Pro', 'add+calc_signals')
    btn_back = getButton(back_txt(), 'go_tariffs')

    keyboard.add(btn_calc, btn_signals)
    keyboard.add(btn_calc_signals, btn_back)
    return keyboard


def kb_admin_tariffs_delete(id: int, page: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_yes = getButton('Нет', 'delete_no', page, id)
    btn_no = getButton('Да', 'delete_yes', page, id)

    keyboard.add(btn_no, btn_yes)
    return keyboard


def kb_admin_tariffs_edit(id: int, page: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_name = getButton('Название', 'edit_name', page, id)
    btn_description = getButton('Описание', 'edit_description', page, id)
    btn_price = getButton('Цена', 'edit_price', page, id)
    btn_image = getButton('Картинку', 'edit_image', page, id)
    btn_duration = getButton('Срок действия', 'edit_duration', page, id)
    btn_findate = getButton('Дату окончания', 'edit_findate', page, id)

    btn_back = getButton(back_txt(), 'list', page, id)

    keyboard.add(btn_name, btn_price)
    keyboard.add(btn_description, btn_image)
    keyboard.add(btn_duration, btn_findate)
    keyboard.add(btn_back)
    return keyboard


def kb_admin_tariffs_list_back(page: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_back = getButton(back_txt(), 'list', page)

    keyboard.add(btn_back)
    return keyboard


def kb_admin_tariffs_back():
    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_back = getButton(back_txt(), 'go_tariffs')

    keyboard.add(btn_back)
    return keyboard
