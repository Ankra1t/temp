from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import user_account_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        user_account_factory.new(type=type)
    )


def kb_user_account():
    keyboard = InlineKeyboardMarkup(row_width=2)
    # btn1 = getButton("Купить сигналы на месяц", 'buy_month')
    btn2 = getButton("Реферальная система", 'referral')
    btn3 = getButton("Мои покупки", 'purchases')
    # btn_password = getButton('Изменить пароль', 'password')
    btn4 = getButton("Главная", 'main')
    # btn5 = getButton("Пополнить баланс")

    # keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)
    return keyboard


def kb_user_referral():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = getButton("Список рефералов", 'referral_list')
    btn2 = getButton("Назад", 'back')

    keyboard.add(btn1, btn2)
    return keyboard

def kb_user_referral_list():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = getButton("Список рефералов", 'referral_list')
    btn2 = getButton("Назад", 'back')

    keyboard.add(btn1, btn2)
    return keyboard