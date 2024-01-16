from telebot import TeleBot
from telebot.types import Message, InlineKeyboardButton

from messages.workers import generate_normal_text
from MAIN.callbacks.admin.posts.keyboards import kb_posts_back


def get_post_from_message(bot: TeleBot, message: Message):
    chat_id = message.chat.id

    mes_type = message.content_type
    if mes_type != 'text' and mes_type != 'video' and mes_type != 'photo':
        bot.send_message(
            chat_id, 'Отправьте пост в виде текста, картинки или видео:',
            reply_markup=kb_posts_back())
        return

    media_id: str | None = None
    
    if (message.content_type == 'photo') and (message.photo is not None):
        media_id = message.photo[-1].file_id
    elif (message.content_type == 'video') and (message.video is not None):
        media_id = message.video.file_id

    return {
        'post': generate_normal_text(message),
        'media_id': media_id,
        'mes_type': mes_type
    }


def get_calculator_btn_link():
    return InlineKeyboardButton("В калькулятор", "https://t.me/fpcalcbot")


def send_in_development(bot: TeleBot, message: Message):
    bot.send_message(
        message.chat.id, 'Временно ведётся разработка❗️\n<b>Следите</b> за обновлениями😉'
    )
