from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import back_txt, cancel_txt

from .filter import livepost_factory


def getButton(text: str, type: str, value=''):
    return InlineKeyboardButton(
        text, None,
        livepost_factory.new(type=type, value=value)
    )


def kb_livepost_cancel():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_cancel = getButton(cancel_txt(), 'cancel')

    keyboard.add(btn_cancel)
    return keyboard


def kb_livepost_type():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_send_now = getButton('Live', 'send_now')
    btn_signal = getButton('Точнее', 'signal')
    btn_cancel = getButton(cancel_txt(), 'cancel')

    keyboard.add(btn_send_now, btn_signal)
    keyboard.add(btn_cancel)
    return keyboard


def kb_livepost_direction():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_all = getButton('Всем', 'send_now', 'all')
    btn_paid = getButton('Платным', 'send_now', 'paid')
    btn_market = getButton('По рынку', 'send_now', 'market')
    btn_time = getButton('Новым', 'send_now', 'time')
    # btn_back = getButton(back_txt(), 'livepost_back')
    btn_cancel = getButton(cancel_txt(), 'cancel')

    keyboard.add(btn_all, btn_paid)
    keyboard.add(btn_market, btn_time)
    keyboard.add(btn_cancel)
    return keyboard


def kb_livepost_time():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_2 = getButton('2 часа', 'send_now', '2h')
    btn_6 = getButton('6 часов', 'send_now', '6h')
    btn_12 = getButton('12 часов', 'send_now', '12h')
    btn_24 = getButton('24 часа', 'send_now', '24h')
    btn_back = getButton(back_txt(), 'send_now')
    btn_cancel = getButton(cancel_txt(), 'cancel')

    keyboard.add(btn_2, btn_6)
    keyboard.add(btn_12, btn_24)
    keyboard.add(btn_back, btn_cancel)
    return keyboard


def kb_livepost_market():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_russia = getButton('РФ', 'send_now', 'RF')
    btn_usa = getButton('США', 'send_now', 'USA')
    btn_forex = getButton('Форекс', 'send_now', 'forex')
    btn_crypto = getButton('Крипта', 'send_now', 'crypto')
    btn_back = getButton(back_txt(), 'send_now', 'send_now')
    btn_cancel = getButton(cancel_txt(), 'cancel')

    keyboard.add(btn_crypto, btn_forex)
    keyboard.add(btn_russia, btn_usa)
    keyboard.add(btn_back, btn_cancel)
    return keyboard
