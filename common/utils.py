import asyncio
from math import floor
import re
from typing import Coroutine, Literal, TypeVar, Any, Callable
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia
from telebot.asyncio_helper import ApiTelegramException

from common.dt import get_str_by_datetime
from data.data import liteDb
from db import db

from models import Price, Post, UserInfo, LANGUAGES_TYPE, Message


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


def check_discount_price(tariff: Price, type: Literal['crypto', 'default'] = 'default'):
    if type == 'default':
        price = tariff.price
    else:
        price = tariff.price_crypto

    if tariff.discount is None:
        return price
    return round(price * (1 - tariff.discount.percent / 100))


async def get_post_from_message(bot: AsyncTeleBot, message: Message, kb_posts_back: Callable[[], InlineKeyboardMarkup]):
    chat_id = message.chat.id

    mes_type = message.content_type
    if mes_type != 'text' and mes_type != 'video' and mes_type != 'photo':
        await bot.send_message(
            chat_id, 'Отправьте пост в виде текста, картинки или видео:',
            reply_markup=kb_posts_back()
        )
        return

    media_id: str | None = None

    if (message.content_type == 'photo') and (message.photo is not None):
        media_id = message.photo[-1].file_id
    elif (message.content_type == 'video') and (message.video is not None):
        media_id = message.video.file_id

    return Post(
        content=get_normal_text(message),
        media=media_id,
        mes_type=mes_type
    )


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


def get_short_user_info(user: UserInfo):
    if user.tg_username != '-' and user.tg_username != '':
        nik = f'| @{user.tg_username} '
    elif user.tg_id > 0:
        nik = f'| {user.tg_id} '
    else:
        nik = ''

    ban = '| (BAN)' if user.ban else ''

    is_set_settings = 0
    calcs_count = len(db.get_calculations_by_user(user.id))

    if calcs_count > 1:
        is_set_settings = 1
    else:
        markets = ('forex', 'RF')
        for el in markets:
            calc_settings = db.get_calc_user_settings(user.id, el, False)
            if calc_settings is not None and calc_settings.deposit is not None and calc_settings.risk is not None:
                is_set_settings = 1
                break

    is_tried = liteDb.getFirstTryUser(user.tg_id)
    user_subsribe = db.get_current_subscribe_user(user.id)

    if user_subsribe is None:
        sub_show = 'нет подписок'
    else:
        fin_date = get_str_by_datetime(user_subsribe.finish_dt)
        type_subscribe_show = f'({user_subsribe.product_type})'
        sub_show = f'<b>{fin_date}</b> {type_subscribe_show}'

    if user.block:
        info = '🅱️ <b>Заблокировал бота</b>'
    else:
        info = f'Подписка до: {sub_show}'

    user_show = (
        f'{user.id} {nik}<b>{ban}</b> | {is_tried} | {is_set_settings}'
        f'\n{info}'
        f'\nЗарегестрирован <b>{get_str_by_datetime(user.registration_dt)}</b>'
    )

    return user_show


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
    if count > 0 and count < 1:
        return two

    n = floor(abs(count))
    n %= 100
    if n >= 5 and n <= 20:
        return five

    n %= 10
    if n == 1:
        return one

    if n >= 2 and n <= 4:
        return two

    return five


def getRuWordEnd(count: float, word: Literal['тейк', 'стоп'] | str):
    if word == 'тейк':
        return getNounByNumber(count, 'тейк', 'тейка', 'тейков')
    if word == 'стоп':
        return getNounByNumber(count, 'стоп', 'стопа', 'стопов')
    return word
