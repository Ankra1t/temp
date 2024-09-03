from typing import Literal
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from common.keyboard import back_txt

from models import CallbackQuery


admin_workers_factory = CallbackData(
    'type', 'id', 'role', prefix='admin_workers'
)


class AdminWorkersCallbackFilter(AdvancedCustomFilter):
    key = 'admin_workers'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str, role: int = -1, id: int = -1):
    return InlineKeyboardButton(
        text, None,
        admin_workers_factory.new(
            type=type,
            id=id,
            role=role
        )
    )


def kb_admin_workers():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_admins = getButton('Админы', 'admins')
    btn_redactors = getButton('Редакторы', 'redactors')
    btn_support = getButton('Поддержка', 'support')
    btn_list = getButton('Список работников', 'workers_list')
    btn_back = getButton(back_txt(), 'go_main')

    keyboard.add(btn_admins, btn_redactors)
    keyboard.add(btn_support, btn_list)
    keyboard.add(btn_back)
    return keyboard


def kb_admin_workers_confirm(id: int, worker: int, action: Literal['add', 'delete']):
    def getThisButton(text: str, type: str):
        return getButton(text, f'{action}_{type}', worker, id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getThisButton('✅ Да', 'yes')
    btn2 = getThisButton('❌ Нет', 'no')

    keyboard.add(btn1, btn2)
    return keyboard


def kb_admin_workers_actions(worker: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('✅ Добавить', 'add', worker)
    btn2 = getButton('❌ Удалить', 'delete', worker)

    btnback = getButton(
        back_txt(), 'workers'
    )

    keyboard.add(btn1, btn2)
    keyboard.add(btnback)
    return keyboard


def kb_admin_workers_back(worker: int = -1):
    keyboard = InlineKeyboardMarkup(row_width=2)

    type = {
        1: 'admins',
        2: 'redactors',
        3: 'support',
        -1: 'workers'
    }
    back_btn = getButton(back_txt(), type[worker])

    keyboard.add(back_btn)
    return keyboard


def kb_admin_workers_support():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_change = getButton('✏️ Изменить', 'update_support')
    btn_back = getButton(back_txt(), 'workers')

    keyboard.add(btn_change, btn_back)
    return keyboard
