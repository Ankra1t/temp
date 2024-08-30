from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter


admin_main_factory = CallbackData('type', prefix='admin_main')


class AdminMainCallbackFilter(AdvancedCustomFilter):
    key = 'admin_main'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        admin_main_factory.new(type=type)
    )


def kb_admin_main():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_users = getButton("Пользователи", 'users')
    btn_workers = getButton("Работники", 'workers')
    btn_posts = getButton("Отложенные посты", 'fut_posts')
    btn_payments = getButton("Оплата", 'payment')
    btn_params = getButton("Параметры", 'params')
    btn_tariffs = getButton("Тарифы", 'tariffs')
    btn_send_settings = getButton("Настройки отправки", 'send_settings')
    btn_site_code = getButton("Войти на сайт", 'site_code')

    keyboard.add(btn_users, btn_workers)
    keyboard.add(btn_posts, btn_payments)
    keyboard.add(btn_params, btn_tariffs)
    keyboard.add(btn_send_settings)
    keyboard.add(btn_site_code)
    return keyboard
