from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt

from .filter import user_tariff_factory


def getButton(text: str, type: str, tariff_id: int | str = ''):
    return InlineKeyboardButton(
        text, None,
        user_tariff_factory.new(
            type=type, tariff_id=tariff_id
        )
    )


def kb_user_tariff_back(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(getButton(back_txt(), 'go_tariff'))
    return keyboard


def kb_tariff_pay(tariff_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    pay_tariff = getButton('💵 Купить', 'pay_tariff', tariff_id)
    btn_back = getButton(back_txt(), 'go_tariff_del')

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


def kb_choose_products():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_signal = getButton(
        'Рекомендация', 'get_tariff', 'signals'
    )
    btn_calc = getButton(
        'Калькулятор', 'get_tariff', 'calc'
    )
    btn_calc_signals = getButton(
        'PRO', 'get_tariff', 'calc_signals'
    )
    btn_back = getButton(back_txt(), 'go_main')

    keyboard.add(btn_signal, btn_calc)
    keyboard.add(btn_calc_signals, btn_back)
    return keyboard
