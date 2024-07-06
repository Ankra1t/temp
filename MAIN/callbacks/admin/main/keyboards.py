from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import admin_main_factory


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
    btn_site_code = getButton("Войти на сайт", 'site_code')
    btn_channel_stats = getButton("Статистика в каналы", 'ch_stats')

    keyboard.add(btn_users, btn_workers)
    keyboard.add(btn_posts, btn_payments)
    keyboard.add(btn_params, btn_tariffs)
    keyboard.add(btn_channel_stats)
    keyboard.add(btn_site_code)
    return keyboard

def kb_channel_stat():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_channel_stats = getButton("Отправить", 'ch_stats_send')
    btn_cancel = getButton("Отмена", 'back')
    keyboard.add(btn_channel_stats, btn_cancel)
    return keyboard
