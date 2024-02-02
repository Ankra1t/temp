from typing import Literal
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from initialize import kb_inl_admin

from .filter import admin_workers_factory


def getButton(text: str, type: str, role: int = -1, id: int | None = None, name: str | None = None):
    return InlineKeyboardButton(
        text, None,
        admin_workers_factory.new(
            type=type,
            id=id,
            name=name,
            role=role
        )
    )


def kb_admin_workers():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_admins = getButton('Гл. админы', 'admins')
    btn_redactors = getButton('Редакторы', 'redactors')
    btn_support = getButton('Тех. поддержка', 'support')
    btn_list = getButton('Список раб.', 'workers_list')
    btn_back = kb_inl_admin.go_main_btn

    keyboard.add(btn_admins, btn_redactors)
    keyboard.add(btn_support, btn_list)
    keyboard.add(btn_back)
    return keyboard


def kb_admin_workers_confirm(id: int, name: str, worker: int, action: Literal['add', 'delete']):
    def getThisButton(text: str, type: str):
        return getButton(text, f'{action}_{type}', worker, id, name)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getThisButton('Да', 'yes')
    btn2 = getThisButton('Нет', 'no')

    keyboard.add(btn1, btn2)
    return keyboard


def kb_admin_workers_actions(worker: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Добавить', 'add', worker)
    btn2 = getButton('Удалить', 'delete', worker)
    btnback = getButton(
        'Назад',
        'admins' if (worker == 1) else 'redactors',
        worker
    )

    keyboard.add(btn1, btn2)
    keyboard.add(btnback)
    return keyboard


def kb_admin_workers_back(worker: int | None = None):
    keyboard = InlineKeyboardMarkup(row_width=2)

    if worker is None:
        worker = -1

    type = {
        1: 'admins',
        2: 'redactors',
        3: 'support',
        -1: 'workers'
    }
    back_btn = getButton('Назад', type[worker])

    keyboard.add(back_btn)
    return keyboard


def kb_admin_workers_support():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_change = getButton('Изменить', 'update_support')
    btn_back = getButton('Назад', 'workers')

    keyboard.add(btn_change, btn_back)
    return keyboard
