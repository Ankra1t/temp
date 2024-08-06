from telebot import TeleBot
from telebot.types import Message

from AuthRoles import check_registrate
from CALCULATE.callbacks.pages import send_admin_channel_calc_item, send_calc_stat_item
from MAIN.callbacks.admin.posts.keyboards import kb_posts_back
from common.utils import delete_message, set_state_data
from MAIN.callbacks import kb_livepost_type
from MAIN.common.utils import get_post_from_message
from MAIN.states import AdminPostsState


def handle_livepost(message: Message, bot: TeleBot):
    mes_id = message.id
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.content_type == 'text' and message.text is not None:
        text = message.text

        if text.startswith('/') and bot.get_state(user_id, chat_id) == 'handle_calc_id':
            delete_message(bot, chat_id, mes_id)

            text = text.replace('/', '')
            if not text.isdigit():
                return

            calc_id = int(text)
            send_admin_channel_calc_item(
                bot, message, user_id, calc_id, is_first=True
            )

            return

        if text.startswith('/') and bot.get_state(user_id, chat_id) == 'user_calc_id':
            delete_message(bot, chat_id, mes_id)

            text = text.replace('/', '')
            if not text.isdigit():
                return

            calc_id = int(text)
            send_calc_stat_item(bot, message, user_id, calc_id, is_first=True)

            return

    # livepost
    user_role = check_registrate(user_id)
    if user_role != 1 and user_role != 2:
        return

    try:
        print(message.html_text)
        if message.animation:
            print(message.animation.file_id)
        if message.photo:
            print(message.photo[-1].file_id)
    except:
        pass

    post = get_post_from_message(bot, message, kb_posts_back)

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
