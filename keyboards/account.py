from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from common.keyboard import back_txt, cancel_txt
from models import LANGUAGES_TYPE


user_account_factory = CallbackData('type', prefix='user_account')


class UserAccountCallbackFilter(AdvancedCustomFilter):
    key = 'user_account'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        user_account_factory.new(type=type)
    )


def kb_user_account(lang: LANGUAGES_TYPE, user_id: int):
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
        },
        'uz': {
            'refs': 'Yo\'naltirish',
            'purchases': 'Mening xaridlarim',
            'params': 'Parametrlar',
            'support': 'Yordam',
            'wallet': 'Hamyon',
        },
        'tr': {
            'refs': 'Referans',
            'purchases': 'Satın alımlarım',
            'params': 'Paramler',
            'support': 'Teknik Destek',
            'wallet': 'Cüzdan',
        },
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
    if user_id == 6919899538:
        keyboard.add(wallet)

    keyboard.add(back)
    return keyboard


def kb_user_referral(lang: LANGUAGES_TYPE, referals_count=0):
    texts = {
        'ru': {
            'refs': 'Список рефералов'
        },
        'en': {
            'refs': 'List of referrals'
        },
        'uz': {
            'refs': 'Yo\'llanmalar'
        },
        'tr': {
            'refs': 'Yönlendirmelerin listesi'
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


def kb_user_referral_list(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(back_txt(lang), 'referral'))
    return keyboard


def kb_user_purchases(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(getButton(back_txt(lang), 'back'))
    return keyboard


def kb_user_params(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'lang': 'Язык',
            'name': 'Изменить имя'
        },
        'en': {
            'lang': 'Language',
            'name': 'Change nickname'
        },
        'uz': {
            'lang': 'Tillar',
            'name': 'Ismni o\'zgartirish'
        },
        'tr': {
            'lang': 'Dil',
            'name': 'İsmini değiştir'
        },
    }

    btn_lang = getButton(f' {texts[lang]["lang"]}', 'set_lang')
    btn_name = getButton(f' {texts[lang]["name"]}', 'set_name')
    btn_back = getButton(back_txt(lang), 'back')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_lang, btn_name, btn_back)
    return keyboard


def kb_params_choose_lang(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'ru': 'Русский',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
        'en': {
            'ru': 'Russian',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
        'uz': {
            'ru': 'Russian',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
        'tr': {
            'ru': 'Russian',
            'en': 'English',
            'uz': 'Uzbek',
            'tr': 'Turkish',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton(f'🇷🇺 {texts[lang]["ru"]}', 'set_lang_ru')
    btn2 = getButton(f'🇺🇸 {texts[lang]["en"]}', 'set_lang_en')
    btn3 = getButton(f'🇺🇿 {texts[lang]["uz"]}', 'set_lang_uz')
    btn4 = getButton(f'🇹🇷 {texts[lang]["tr"]}', 'set_lang_tr')
    btn_back = getButton(cancel_txt(lang), 'params')

    keyboard.add(btn1, btn2, btn3, btn4)
    keyboard.add(btn_back)
    return keyboard


def kb_user_params_back(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_back = getButton(cancel_txt(lang), 'params')
    keyboard.add(btn_back)
    return keyboard


def kb_support(lang: LANGUAGES_TYPE, link: str):
    link = link.replace('@', '')

    texts = {
        'ru': {
            'operator': 'Оператор',
            'news': 'Новости',
        },
        'en': {
            'operator': 'Support',
            'news': 'News',
        },
        'uz': {
            'operator': 'Qo\'llab-quvvatlash',
            'news': 'Yangiliklar',
        },
        'tr': {
            'operator': 'Destek',
            'news': 'Haberler',
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


def kb_wallets(lang: LANGUAGES_TYPE, wallets: list[str]):
    row_width = 2

    back = getButton(back_txt(lang), 'back')
    wal_buttons = [getButton(el, f'connect++{el}') for el in wallets]

    keyboard = InlineKeyboardMarkup(row_width=row_width)
    keyboard.add(*wal_buttons, back)
    return keyboard


def kb_wallet_connect(lang: LANGUAGES_TYPE, url: str):
    texts = {
        'ru': 'Подключить',
        'en': 'Connect',
        'uz': 'Ulanmoq',
        'tr': 'Bağlamak',
    }

    back = getButton(back_txt(lang), 'wallet')
    url_btn = InlineKeyboardButton(texts[lang], url)
    btn_check = getButton('CHECK', 'wallet_check')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(url_btn, btn_check, back)
    return keyboard
