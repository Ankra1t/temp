from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt
from common.utils import get_lang

from .filter import user_tariff_factory


def getButton(text: str, type: str, tariff_id: int | str = '', tariff_type='', page: int = 0):
    return InlineKeyboardButton(
        text, None,
        user_tariff_factory.new(
            type=type, tariff_id=tariff_id, page=page, tariff_type=tariff_type
        )
    )


def kb_user_tariff_back(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(getButton(back_txt(lang), 'go_main'))
    return keyboard


def kb_tariff_list(user_id: int, tariff_id: int, count: int, tariff_type: str, page=0):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=3)

    texts = {
        'ru': {
            'next': 'Вперед',
            'prev': 'Назад',
            'buy': 'Купить',
        },
        'en': {
            'next': 'Next',
            'prev': 'Back',
            'buy': 'Buy',
        }
    }

    if count > 1:
        if page + 1 == count:
            next_page = 0
        else:
            next_page = page + 1

        if page == 0:
            prev_page = count - 1
        else:
            prev_page = page - 1

        btn_next = getButton(
            texts[lang]['next'],
            'get_tariff', '', tariff_type, next_page
        )
        btn_prev = getButton(
            texts[lang]['prev'],
            'get_tariff', '', tariff_type, prev_page
        )
        counter = getButton(f'{page + 1}/{count}', 'counter')
        keyboard.add(btn_prev, counter, btn_next)

    pay_tariff = getButton(
        f'💵 {texts[lang]["buy"]}', 'pay_tariff', tariff_id, tariff_type, page
    )
    btn_back = getButton(back_txt(lang), 'go_main')

    keyboard.add(pay_tariff, btn_back)
    return keyboard


pays_translate = {
    'ru': {
        'cp': 'Оплатить через CryptoBot',
        'bb': 'Оплатить через BitBanker'
    },
    'en': {
        'cp': 'Pay via CryptoBot',
        'bb': 'Pay via BitBanker'
    }
}

def kb_bill(user_id: int, yookassa_price: str, url_yookassa: str, cryptobot_price: str, url_cryptobot: str):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    text = {
        'ru': {
            'yoo': f'Оплатить {yookassa_price} через юКассу',
            'cp': f'Оплатить {cryptobot_price} через CryptoBot'
        },
        'en': {
            'yoo': f'Pay {yookassa_price} via yooKassa',
            'cp': f'Pay {cryptobot_price} via CryptoBot'
        },
    }

    if url_yookassa != '':
        keyboard.add(
            InlineKeyboardButton(
                text[lang]['yoo'], url_yookassa
            )
        )

    if url_cryptobot != '':
        keyboard.add(
            InlineKeyboardButton(
                text[lang]['cp'], url_cryptobot
            )
        )

    btn_back = getButton(back_txt(lang), 'go_tariff')
    keyboard.add(btn_back)
    return keyboard


def kb_choose_products(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'signals': 'Рекомендации',
            'calc': 'Калькулятор',
            'pro': 'PRO'
        },
        'en': {
            'signals': 'Recommendations',
            'calc': 'Calculator',
            'pro': 'PRO'
        }
    }

    btn_signal = getButton(
        texts[lang]['signals'], 'get_tariff', tariff_type='signals'
    )
    btn_calc = getButton(
        texts[lang]['calc'], 'get_tariff', tariff_type='calc'
    )
    btn_calc_signals = getButton(
        texts[lang]['pro'], 'get_tariff', tariff_type='calc_signals'
    )
    btn_back = getButton(back_txt(lang), 'go_main')

    # keyboard.add(btn_signal, btn_calc)
    # keyboard.add(btn_calc_signals, btn_back)
    keyboard.add(btn_calc, btn_back)
    return keyboard
