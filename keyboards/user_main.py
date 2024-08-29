from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter

from config_global import SITE_URL
from models import LANGUAGES_TYPE

from common.utils import get_calculator_btn_link
from common.keyboard import back_txt


user_main_factory = CallbackData('type', prefix='user_main')


class UserMainCallbackFilter(AdvancedCustomFilter):
    key = 'user_main'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, user_main_factory.new(type=type))


def kb_user_main(lang: LANGUAGES_TYPE, new_user=False):
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'try': 'Попробовать расчёт',
            'buy': 'Купить',
            'calc': 'Калькулятор',
            'account': 'Личный кабинет',
            'site': 'Войти на сайт',
            'channel': 'Канал',
        },
        'en': {
            'try': 'Try the calculation',
            'buy': 'Buy',
            'calc': 'Calculator',
            'account': 'Profile',
            'site': 'Go to the website',
            'channel': 'Сhannel',
        },
        'uz': {
            'try': 'Hisoblashni sinab ko\'ring',
            'buy': 'Sotib olish',
            'calc': 'Kalkulyator',
            'account': 'Shaxsiy kabinet',
            'site': 'Saytga kiring',
            'channel': 'Rohanna',
        },
        'tr': {
            'try': 'Hesaplamayı deneyin',
            'buy': 'Satın al',
            'calc': 'Hesap makinesi',
            'account': 'Kişisel Hesap',
            'site': 'Siteye giriş yap',
            'channel': 'kanal',
        },
    }

    # btn1 = getButton("Рекомендации", 'signals')
    # btn_buy = getButton(f"💰 {texts[lang]['buy']}", 'buy')
    btn_try = getButton(f"✏️ {texts[lang]['try']}", 'try')
    # btn3 = getButton("Обучение", 'education')
    btn_calc = getButton(f"⌨️ {texts[lang]['calc']}", 'calculator')
    btn_account = getButton(f"{texts[lang]['account']}", 'account')
    # btn_site = getButton(f"{texts[lang]['site']}", 'site')

    news_link = 'my_investors' if lang == 'ru' else 'my_traders'
    btn_channel = InlineKeyboardButton(
        texts[lang]['channel'], f'https://t.me/{news_link}'
    )

    if new_user:
        keyboard.add(btn_try)
    else:
        keyboard.add(btn_calc)
        keyboard.add(btn_channel, btn_account)

    return keyboard


def kb_user_calculator(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(get_calculator_btn_link(lang))
    return keyboard


def kb_site_login(lang: LANGUAGES_TYPE, code: str, is_reset=False):
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'site': 'Войти на сайт',
        },
        'en': {
            'site': 'Go to the website',
        },
        'uz': {
            'site': 'Saytga kiring',
        },
        'tr': {
            'site': 'Siteye giriş yap',
        },
    }

    btn_link = InlineKeyboardButton(
        texts[lang]['site'], url=f'{SITE_URL}/auth/tg?code={code}'
    )
    btn_reset = getButton('✅' if is_reset else '🔄', 'site_reset')
    btn_back = getButton(back_txt(lang), 'main')

    buttons = []
    if code:
        buttons.append(btn_link)
    buttons.append(btn_reset)
    buttons.append(btn_back)

    keyboard.add(*buttons)
    return keyboard
