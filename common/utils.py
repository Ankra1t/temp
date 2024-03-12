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


def get_lang(tg_id: int):
    user_db_id = db_new.get_user_id_by_tg_id(tg_id)
    return db_new.get_user_lang(user_db_id) or 'ru'


def get_print_float(value: float, round_count: int | None = None):
    if int(value) == value:
        return int(value)

    if round_count is not None:
        return round(value, min(round_count, 5))

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


def get_calculation(
    deposit: float,
    risk_value: float,
    open_price: float,
    stop_loss: float,
    split_values: list[float] | None,
    ticker: str | None = None,
    tp_ratio: list[int] = [3, 4, 5],
):
    """
    Returns:
        count_bet, value_bet, credit, take_profit, profit
    """

    if open_price == stop_loss:
        stop_loss = open_price - 0.01

    # Разница цены входа и стоп-лосса
    diff_op_sl = abs(open_price - stop_loss)

    rate = 1
    if ticker is not None:
        fut = db_new.get_future(ticker)
        rate = fut.price_step if (fut is not None) else 1

    # Кол-во покупки
    count_bet = risk_value / diff_op_sl * rate

    # Сумма покупки
    value_bet = count_bet * open_price

    # Подсчет кридитного плеча
    credit = 1
    if value_bet > deposit:
        credit = int(value_bet // deposit + 1)

    take_profit: list[float] = []
    profit: list[float] = []
    for i, el in enumerate(tp_ratio):
        take_profit.append(open_price + (open_price - stop_loss) * el)

        rate = 1
        if split_values is not None:
            rate = split_values[i] / 100

        profit.append(risk_value * el * rate)

    return count_bet, value_bet, credit, take_profit, profit
