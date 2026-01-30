from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from models import CallbackQuery

admin_main_factory = CallbackData('type', 'value', prefix='admin_main')


class AdminMainCallbackFilter(AdvancedCustomFilter):
    key = 'admin_main'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str, value: str = ''):
    return InlineKeyboardButton(
        text, None,
        admin_main_factory.new(type=type, value=value)
    )


def kb_admin_main():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_users = getButton("Пользователи", 'users')
    btn_subs = getButton("Подписки", 'subs')
    btn_payments = getButton("Оплата", 'payment')
    btn_params = getButton("Параметры", 'params')
    btn_send_settings = getButton("Настройки отправки", 'send_settings')
    btn_site_code = getButton("Войти на сайт", 'site_code')

    keyboard.add(btn_users, btn_subs)
    keyboard.add(btn_payments, btn_params)
    keyboard.add(btn_send_settings)
    keyboard.add(btn_site_code)
    return keyboard
