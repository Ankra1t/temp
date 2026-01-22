from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from common.keyboard import back_txt
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
    btn_workers = getButton("Работники", 'workers')
    btn_posts = getButton("Отложенные посты", 'fut_posts')
    btn_payments = getButton("Оплата", 'payment')
    btn_params = getButton("Параметры", 'params')
    btn_send_settings = getButton("Настройки отправки", 'send_settings')
    btn_get_tickers = getButton("Список монет", 'tools')
    btn_site_code = getButton("Войти на сайт", 'site_code')

    keyboard.add(btn_users, btn_subs)
    keyboard.add(btn_workers, btn_payments)
    keyboard.add(btn_params)
    keyboard.add(btn_posts, btn_send_settings)
    keyboard.add(btn_get_tickers, btn_site_code)
    return keyboard


def kb_admin_tools_list(turnover: str = ''):
    return InlineKeyboardMarkup(row_width=2).add(
        getButton('⬇️ Бессрочные.P', 'tools_spot', turnover),
        getButton('⬇️ Спот', 'tools_default', turnover),
        getButton('Оборот от...', 'tools_turnover', turnover),
        getButton(back_txt(), 'back')
    )


def kb_tools_list_back(turnover: str = ''):
    return InlineKeyboardMarkup().add(
        getButton(back_txt(), 'tools', turnover)
    )
