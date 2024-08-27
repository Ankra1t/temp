from telebot import TeleBot
from telebot.types import CallbackQuery

from models import MANUAL_TYPE
from messages.common import msg_manuals

from .filter import manual_factory, ManualCallbackFilter
from pages.calculate import send_main, send_manual


def _manual_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = manual_factory.parse(call.data)
    type = callback_data['type']
    page = int(callback_data['page'])

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'main':
        send_main(call.message, bot, user_id)

    if 'manual' in type:
        type_arr = type.split('+')
        manual_type: MANUAL_TYPE = 'calc'
        if len(type_arr) == 2:
            manual_type = type_arr[1] # type: ignore

        send_manual(bot, call.message, user_id, manual_type)

    if type == 'prev':
        page -= 1
    elif type == 'next':
        page += 1
    elif type == 'start':
        page = 1
    elif type == 'end':
        page = len(msg_manuals)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(ManualCallbackFilter())
    bot.register_callback_query_handler(
        _manual_callback_handler,
        lambda _: True, pass_bot=True,
        manual=manual_factory.filter())
