from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt
from common.utils import get_lang

from .filter import user_account_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        user_account_factory.new(type=type)
    )


def kb_user_account(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'refs': 'Рефералка',
            'purchases': 'Мои покупки',
        },
        'en': {
            'refs': 'Referral',
            'purchases': 'My purchases',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    referral = getButton(f"🌐 {texts[lang]['refs']}", 'referral')
    purchases = getButton(f"🛍 {texts[lang]['purchases']}", 'purchases')
    # password = getButton('Изменить пароль', 'password')
    back = getButton(back_txt(lang), 'main')
    # btn5 = getButton("Пополнить баланс")

    keyboard.add(purchases, referral)
    keyboard.add(back)
    return keyboard


def kb_user_referral(user_id: int, referals_count=0):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'refs': 'Список рефералов'
        },
        'en': {
            'refs': 'List of referrals'
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_list = getButton(f"📋 {texts[lang]['refs']}", 'referral_list')
    btn_back = getButton(back_txt(lang), 'back')

    if referals_count == 0:
        keyboard.add(btn_back)
    else:
        keyboard.add(btn_list, btn_back)

    return keyboard


def kb_user_referral_list(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup()

    btn_back = getButton(back_txt(lang), 'referral')

    keyboard.add(btn_back)
    return keyboard


def kb_user_purchases(user_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(back_txt(lang), 'back'))
    return keyboard
