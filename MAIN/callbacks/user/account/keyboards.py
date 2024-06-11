from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt, cancel_txt
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
            'params': 'Параметры',
            'support': 'Тех. поддержка',
            'wallet': 'Кошелёк',
        },
        'en': {
            'refs': 'Referral program',
            'purchases': 'My purchases',
            'params': 'Params',
            'support': 'Support',
            'wallet': 'Wallet',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_support = getButton(f"{texts[lang]['support']}", 'support')
    referral = getButton(f"🌐 {texts[lang]['refs']}", 'referral')
    purchases = getButton(f"🛍 {texts[lang]['purchases']}", 'purchases')
    params = getButton(f"🛠 {texts[lang]['params']}", 'params')
    # password = getButton('Изменить пароль', 'password')
    wallet = getButton(texts[lang]['wallet'], 'wallet')
    back = getButton(back_txt(lang), 'main')
    # btn5 = getButton("Пополнить баланс")

    keyboard.add(purchases, referral)
    keyboard.add(params, btn_support)
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


def kb_user_params(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'lang': 'Язык',
            'name': 'Изменить имя'
        },
        'en': {
            'lang': 'Language',
            'name': 'Change name'
        },
    }

    btn_lang = getButton(f' {texts[lang]["lang"]}', 'set_lang')
    btn_name = getButton(f' {texts[lang]["name"]}', 'set_name')
    btn_back = getButton(back_txt(lang), 'back')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_lang, btn_name, btn_back)
    return keyboard


def kb_params_choose_lang(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'ru': 'Русский',
            'en': 'English',
        },
        'en': {
            'ru': 'Russian',
            'en': 'English',
        }
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'🇷🇺 {texts[lang]["ru"]}', 'set_lang_ru')
    btn2 = getButton(f'🇺🇸 {texts[lang]["en"]}', 'set_lang_en')
    btn_back = getButton(cancel_txt(lang), 'params')

    keyboard.add(btn1, btn2)
    keyboard.add(btn_back)
    return keyboard


def kb_user_params_back(user_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_back = getButton(cancel_txt(lang), 'params')
    keyboard.add(btn_back)
    return keyboard


def kb_support(user_id: int, link: str):
    link = link.replace('@', '')
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'operator': 'Оператор',
            'news': 'Новости',
        },
        'en': {
            'operator': 'Support',
            'news': 'News',
        },
    }

    news_link = 'profmarkets' if lang == 'ru' else 'promarketsen'
    btn_news = InlineKeyboardButton(
        texts[lang]['news'], f'https://t.me/{news_link}'
    )

    btn_link = InlineKeyboardButton(
        texts[lang]['operator'], f'https://t.me/{link}'
    )
    btn_back = getButton(back_txt(lang), 'main')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_link, btn_news, btn_back)
    return keyboard