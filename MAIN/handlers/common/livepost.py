from telebot import TeleBot
from telebot.types import Message

from common.utils import set_state_data
from MAIN.callbacks import kb_livepost_type
from MAIN.common.utils import get_post_from_message
from MAIN.states import AdminPostsState


def handle_livepost(message: Message, bot: TeleBot, data: dict[str, str]):
    user_role = data.get('user_role', 0)
    if user_role != 1 and user_role != 2:
        return

    try:
        print(message.html_text)
        if message.animation:
            print(message.animation.file_id)
    except:
        pass

    chat_id = message.chat.id
    user_id = message.from_user.id

    post = get_post_from_message(bot, message)

    if post is None:
        return

    state_data = {'post': post, 'kind': 'live'}
    bot.set_state(user_id, AdminPostsState.live, chat_id)
    set_state_data(bot, user_id, chat_id, state_data)

    bot.send_message(
        chat_id, 'Выберите действие:',
        reply_markup=kb_livepost_type()
    )


def registration(bot: TeleBot):
    bot.register_message_handler(
        handle_livepost,
        content_types=['photo', 'video', 'text', 'animation'],
        pass_bot=True
    )
