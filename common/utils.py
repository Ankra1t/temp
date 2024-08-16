from telebot.types import Message, InlineKeyboardMarkup, InputMedia
from telebot import TeleBot
from typing import Literal, TypeVar, Any
import re

from config_logger import logger

from db import db
from models import Price


T = TypeVar('T', int, float)

digit_pattern = r'^[+-]?((\d+[\.,]?\d*)|([\.,]\d+))$'

def is_digit(val: str) -> bool:
    return re.search(digit_pattern, val) is not None


def digit_accept(message: Message, type: type[T] = float):
    value = message.text

    if message.content_type == 'text' and value is not None and is_digit(value):
        value = value.replace(',', '.')
        if '.' not in value and value.startswith('0'):
            value = '0.' + value[1:]

        return type(float(value))


def text_accept(message: Message):
    if message.content_type == 'text' and message.text is not None:
        return message.text


def set_state_data(bot: TeleBot, user_id: int, chat_id: int, value: dict[str, Any]):
    try:
        with bot.retrieve_data(user_id, chat_id) as data:
            for key in value:
                data[key] = value[key]
    except Exception as e:
        logger.error(f'Ошибка в записи данных state [{key} {value}] [{e}]')


def edit_message(
    bot: TeleBot,
    message: Message,
    type: Literal['photo', 'text', 'video', 'animation'],
    text: str,
    markup: InlineKeyboardMarkup | None = None,
    media: Any = None
):
    chat_id = message.chat.id
    mes_id = message.id

    new_mes_id = mes_id

    if message.content_type == 'text' and type == 'text':
        bot.edit_message_text(
            text, chat_id, mes_id, reply_markup=markup
        )
    elif message.content_type != 'text' and type != 'text':
        bot.edit_message_media(
            InputMedia(type, media, text, 'HTML'),
            chat_id, mes_id,
            reply_markup=markup
        )
    else:
        delete_message(bot, chat_id, mes_id)
        if type == 'text':
            new_mes = bot.send_message(chat_id, text, reply_markup=markup)
            new_mes_id = new_mes.id
        elif type == 'video':
            new_mes = bot.send_video(
                chat_id, media,
                caption=text,
                reply_markup=markup
            )
            new_mes_id = new_mes.id
        elif type == 'animation':
            bot.send_animation(
                chat_id, media, caption=text,
                reply_markup=markup
            )
        elif type == 'photo':
            new_mes = bot.send_photo(
                chat_id, media, text,
                reply_markup=markup
            )
            new_mes_id = new_mes.id

    return new_mes_id


def delete_message(
    bot: TeleBot,
    chat_id: int,
    mes_id: int,
):
    try:
        return bot.delete_message(chat_id, mes_id)
    except:
        return False


def get_lang(tg_id: int):
    user_db_id = db.get_user_id_by_tg_id(tg_id)
    return db.get_user_lang(user_db_id) or 'ru'


def get_print_float(value: float, round_count: int | None = None):
    def del_nulls(val: str) -> str:
        if ('.' in val and val.endswith('0')) or val.endswith('.'):
            return del_nulls(val[:-1])

        return val

    if int(value) == value:
        return str(int(value))

    if round_count is not None:
        result = round(value, round_count)
        if result == int(result):
            return str(int(result))

        return del_nulls(f'{result:.{round_count}f}')

    if round(value, 2) == value:
        return del_nulls(str(round(value, 2)))

    if round(value, 3) == value:
        return del_nulls(str(round(value, 3)))

    return del_nulls(str(round(value, 4)))


def get_decimal_count(value: float):
    num_str = str(value)

    try:
        dot_index = num_str.index('.')

        if 'e' in num_str:
            e_index = num_str.index('e')
            decimal_count = e_index - dot_index - 1
            return abs(int(num_str[e_index + 1:])) + decimal_count
    except:
        return 0

    num_digits = len(num_str) - dot_index - 1
    return num_digits


def get_normal_text(message: Message):
    return message.html_text or message.html_caption or ''


def check_discount_price(tariff: Price, type: Literal['crypto', 'default']='default'):
    if type == 'default':
        price = tariff.price
    else:
        price = tariff.price_crypto

    if tariff.discount is None:
        return price
    return round(price * (1 - tariff.discount.percent / 100))
