from telebot import TeleBot
from telebot.types import CallbackQuery

from Classes.BlockTGBotSender import BlockTGBotSender

from MAIN.states import AdminPostsState
from MAIN.callbacks import send_admin_main
from models import Post

from .filter import livepost_factory, LivepostCallbackFilter
from .keyboards import kb_livepost_cancel

def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = livepost_factory.parse(call.data)
    type = data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'cancel':
        bot.edit_message_text('Отменено!', chat_id, mes_id)
        send_admin_main(bot, call.message, user_id, True)

    if type == 'signal':
        bot.edit_message_text(
            'Введите название рекомендации:',
            chat_id, mes_id,
            reply_markup=kb_livepost_cancel()
        )
        bot.set_state(user_id, AdminPostsState.name, chat_id)

    if type == 'send_now':
        bot.edit_message_text('Отправка...', chat_id, mes_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            post: Post = data.get('post')

        tg_sender = BlockTGBotSender([], post)
        tg_sender.send()

        bot.edit_message_text('Успешно отправлен!', chat_id, mes_id)
        bot.delete_state(user_id, chat_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(LivepostCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        livepost=livepost_factory.filter()
    )
