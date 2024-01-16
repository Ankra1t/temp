from typing import Literal
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import admin_workers_factory

# TODO - удалить
from initialize import kb_inl_admin


def kb_admin_workers_update(id: int, name: str, role: Literal[1, 2], action: Literal['add', 'delete']):
    def getButton(text: str, type: str):
        return InlineKeyboardButton(
            text, None,
            admin_workers_factory.new(type=f'{action}_{type}', id=id, name=name, role=role))

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Да', 'yes')
    btn2 = getButton('Нет', 'no')

    keyboard.add(btn1, btn2)
    return keyboard


def kb_admin_workers_actions(worker: str):
    def getButton(text: str, type: str):
        return InlineKeyboardButton(
            text, None,
            admin_workers_factory.new(
                type=type, id='', name='',
                role='1' if worker == 'admin' else '2')
        )

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Добавить', 'add')
    btn2 = getButton('Удалить', 'delete')
    btn3 = getButton('Список', f'{worker}_list')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    keyboard.add(kb_inl_admin.go_workers_btn, kb_inl_admin.go_main_btn)
    return keyboard
