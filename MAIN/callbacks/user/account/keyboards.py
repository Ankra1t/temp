from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt

from .filter import user_account_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        user_account_factory.new(type=type)
    )


def kb_user_account():
    keyboard = InlineKeyboardMarkup(row_width=2)

    referral = getButton("🌐 Рефералка", 'referral')
    purchases = getButton("🛍 Мои покупки", 'purchases')
    # password = getButton('Изменить пароль', 'password')
    back = getButton(back_txt(), 'main')
    # btn5 = getButton("Пополнить баланс")

    keyboard.add(purchases, back)
    return keyboard


def kb_user_referral():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton("📋 Список рефералов", 'referral_list')
    btn2 = getButton(back_txt(), 'back')

    keyboard.add(btn1, btn2)
    return keyboard


def kb_user_referral_list():
    keyboard = InlineKeyboardMarkup()

    btn_back = getButton("Назад", 'referral')

    keyboard.add(btn_back)
    return keyboard
