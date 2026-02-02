from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from models import LANGUAGES_TYPE, CallbackQuery


user_main_factory = CallbackData('type', prefix='user_main')


class UserMainCallbackFilter(AdvancedCustomFilter):
    key = 'user_main'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
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
    btn_try = getButton(f"✏️ {texts[lang]['try']}", 'try')
    # btn3 = getButton("Обучение", 'education')
    btn_calc = getButton(f"⌨️ {texts[lang]['calc']}", 'calculator')
    btn_account = getButton(f"{texts[lang]['account']}", 'account')

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
