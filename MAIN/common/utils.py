from telebot import TeleBot
from telebot.types import Message, InlineKeyboardButton
from common.dt import get_str_by_datetime

from db import db
from common.utils import get_decimal_count, get_print_float, get_normal_text
from MAIN.callbacks.admin.posts.keyboards import kb_posts_back
from models import Post, UserInfo


def get_post_from_message(bot: TeleBot, message: Message):
    chat_id = message.chat.id

    mes_type = message.content_type
    if mes_type != 'text' and mes_type != 'video' and mes_type != 'photo':
        bot.send_message(
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


def get_calculator_btn_link():
    return InlineKeyboardButton("⌨️ В калькулятор", "https://t.me/fpcalcbot")


def send_in_development(bot: TeleBot, message: Message):
    bot.send_message(
        message.chat.id, 'Временно ведётся разработка❗️\n<b>Следите</b> за обновлениями😉'
    )


def get_print_signal_info(open_price: float, stop_loss: float):
    round_count = max(
        get_decimal_count(open_price),
        get_decimal_count(stop_loss)
    )

    return '\n'.join((
        f'Цена входа: <b>{get_print_float(open_price, round_count)}</b>',
        f'Стоп лосс: <b>{get_print_float(stop_loss, round_count)}</b>'
    ))


def get_short_user_info(user: UserInfo):
    if user.username != '':
        nik = f'| @{user.username} '
    elif user.tg_id > 0:
        nik = f'| {user.tg_id} '
    else:
        nik = ''

    ban = '| (BAN)' if user.ban == 1 else ''

    user_subsribe = db.get_current_subscribe_user(user.id)

    if user_subsribe is None:
        sub_show = 'нет подписок'
    else:
        fin_date = get_str_by_datetime(user_subsribe.finish_dt)
        type_subscribe_show = f'({user_subsribe.type})'
        sub_show = f'<b>{fin_date}</b> {type_subscribe_show}'

    user_show = (
        f'{user.id} {nik}<b>{ban}</b>'
        f'\nПодписка до: {sub_show}'
        f'\nЗарегестрирован <b>{get_str_by_datetime(user.registration_dt)}</b>'
    )

    return user_show
