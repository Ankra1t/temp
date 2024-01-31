import re
from telebot import TeleBot
from telebot.types import Message
from typing import TypeVar, Any

from db_new import db_new


T = TypeVar('T', int, float)

digit_pattern = r'^[+-]?((\d+[\.,]?\d*)|([\.,]\d+))$'
def is_digit(val: str) -> bool:
    return re.search(digit_pattern, val) is not None


def digit_accept(message: Message, type: type[T] = float):
    if message.content_type == 'text' and message.text is not None and is_digit(message.text):
        return type(float(message.text.replace(',', '.')))


def text_accept(message: Message):
    if message.content_type == 'text' and message.text is not None:
        return message.text


def set_state_data(bot: TeleBot, user_id: int, chat_id: int, value: dict[str, Any]):
    try:
        with bot.retrieve_data(user_id, chat_id) as data:
            for key in value:
                data[key] = value[key]
    except Exception as e:
        print(f'Ошибка в записи данных state [{e}]')


def float_to_print(val: float | None):
    return round(val, 2) if val is not None else '-'


def get_lang(tg_id: int):
    user_db_id = db_new.get_user_id_by_tg_id(tg_id)
    return db_new.get_user_lang(user_db_id) or 'ru'


def get_print_float(value: float, round_count: int | None = None):
    if int(value) == value:
        return int(value)

    if round_count is not None:
        return round(value, round_count)

    if round(value, 2) == value:
        return round(value, 2)

    if round(value, 3) == value:
        return round(value, 3)

    return round(value, 4)


def get_decimal_count(value: float):
    num_str = str(value)
    decimal_index = num_str.index('.')
    num_digits = len(num_str) - decimal_index - 1
    return num_digits

def get_normal_text(message: Message):
    return message.html_text or message.html_caption or ''