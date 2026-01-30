import asyncio
import re
from typing import Coroutine, Literal, TypeVar, Any, Callable
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia
from telebot.asyncio_helper import ApiTelegramException

from models import LANGUAGES_TYPE, Message


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


async def edit_message(
    bot: AsyncTeleBot,
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
        await bot.edit_message_text(
            text, chat_id, mes_id, reply_markup=markup
        )
    elif message.content_type != 'text' and type != 'text':
        await bot.edit_message_media(
            InputMedia(type, media, text, 'HTML'),
            chat_id, mes_id,
            reply_markup=markup
        )
    else:
        await delete_message(bot, chat_id, mes_id)
        if type == 'text':
            new_mes = await bot.send_message(chat_id, text, reply_markup=markup)
            new_mes_id = new_mes.id
        elif type == 'video':
            new_mes = await bot.send_video(
                chat_id, media,
                caption=text,
                reply_markup=markup
            )
            new_mes_id = new_mes.id
        elif type == 'animation':
            await bot.send_animation(
                chat_id, media, caption=text,
                reply_markup=markup
            )
        elif type == 'photo':
            new_mes = await bot.send_photo(
                chat_id, media, text,
                reply_markup=markup
            )
            new_mes_id = new_mes.id

    return new_mes_id


async def delete_message(
    bot: AsyncTeleBot,
    chat_id: int,
    mes_id: int,
):
    try:
        return await bot.delete_message(chat_id, mes_id)
    except:
        return False


def get_lang(tgId=1):
    return 'ru'


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


def get_calculator_btn_link(lang: LANGUAGES_TYPE):
    text = {
        'ru': 'В калькулятор',
        'en': 'To calculator',
    }

    return InlineKeyboardButton(f"⌨️ {text[lang]}", "https://t.me/fpcalcbot")


async def send_in_development(bot: AsyncTeleBot, message: Message):
    await bot.send_message(
        message.chat.id, 'Временно ведётся разработка❗️\n<b>Следите</b> за обновлениями😉'
    )


def get_print_signal_info(open_price: float, stop_loss: float):
    round_count = max(
        get_decimal_count(open_price),
        get_decimal_count(stop_loss)
    )

    return '\n'.join((
        f'Цена входа: <b>{get_print_float(open_price, round_count)}</b>',
        f'Стоп-лосс: <b>{get_print_float(stop_loss, round_count)}</b>'
    ))


T = TypeVar("T")


async def antiflood(function: Callable[..., Coroutine[Any, Any, T]], *args, number_retries=15, **kwargs) -> T:
    for _ in range(number_retries - 1):
        try:
            return await function(*args, **kwargs)
        except ApiTelegramException as ex:
            if ex.error_code == 429:
                await asyncio.sleep(ex.result_json['parameters']['retry_after'])
            else:
                raise
    else:
        return await function(*args, **kwargs)


def getNounByNumber(count: float, one: str, two: str, five: str):
    count = abs(count)

    count %= 100
    if count >= 5 and count <= 20:
        return five

    count %= 10
    if count == 1:
        return one

    if count > 0 and count <= 4:
        return two

    return five


def format_number(n: float | int):
    if n < 1000:
        return get_print_float(n, 0)
    elif n < 1000000:
        return "{:.1f}K".format(n / 1000)
    elif n < 1000000000:
        return "{:.1f}M".format(n / 1000000)
    else:
        return "{:.1f}B".format(n / 1000000000)
