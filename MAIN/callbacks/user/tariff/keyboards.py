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
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(getButton(back_txt(), 'go_tariff'))
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

        btn_next = getButton(texts[lang]['next'],
                             'get_tariff', '', tariff_type, next_page)
        btn_prev = getButton(texts[lang]['prev'],
                             'get_tariff', '', tariff_type, prev_page)
        counter = getButton(f'{page + 1}/{count}', 'counter')
        keyboard.add(btn_prev, counter, btn_next)

    pay_tariff = getButton(
        f'💵 {texts[lang]["buy"]}', 'pay_tariff', tariff_id, tariff_type, page
    )
    btn_back = getButton(back_txt(lang), 'go_tariff_del')

    keyboard.add(pay_tariff, btn_back)
    return keyboard


def kb_bill_cryptobot(price: str, pay_link: str):
    keyboard = InlineKeyboardMarkup(row_width=2)

    pay_link_btn = InlineKeyboardButton(
        f"Оплатить {price} через CryptoBot", pay_link
    )
    btn_back = getButton(back_txt(), 'go_tariff')

    keyboard.add(pay_link_btn)
    keyboard.add(btn_back)
    return keyboard


def kb_bill_bitbanker(price: str, pay_link: str):
    keyboard = InlineKeyboardMarkup(row_width=2)

    pay_link_btn = InlineKeyboardButton(
        f"Оплатить {price} через BitBanker", pay_link
    )
    btn_back = getButton(back_txt(), 'go_tariff')

    keyboard.add(pay_link_btn)
    keyboard.add(btn_back)
    return keyboard


def kb_bill_many(price: str, pay_link_cryptobot: str, pay_link_bitbanker: str):
    keyboard = InlineKeyboardMarkup(row_width=1)

    pay_link_btn1 = InlineKeyboardButton(
        f"Оплатить {price} через CryptoBot", pay_link_cryptobot
    )
    pay_link_btn2 = InlineKeyboardButton(
        f"Оплатить {price} через BitBanker", pay_link_bitbanker
    )
    btn_back = getButton(back_txt(), 'go_tariff')

    keyboard.add(pay_link_btn2)
    keyboard.add(pay_link_btn1)
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
