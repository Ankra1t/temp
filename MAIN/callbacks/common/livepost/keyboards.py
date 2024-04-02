from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt

from .filter import livepost_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        livepost_factory.new(type=type)
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