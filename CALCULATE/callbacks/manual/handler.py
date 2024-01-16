from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.common.messages import msg_manual

from .filter import manual_factory, ManualCallbackFilter
from ..pages import send_manual_page


def _manual_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = manual_factory.parse(call.data)
    type = callback_data['type']
    page = int(callback_data['page'])

    if type == 'prev':
        page -= 1
    if type == 'next':
        page += 1
    if type == 'start':
        page = 1
    if type == 'end':
        page = len(msg_manual)

    if type != 'counter':
        send_manual_page(call.message, bot, page, call.from_user.id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(ManualCallbackFilter())
    bot.register_callback_query_handler(
        _manual_callback_handler,
        lambda _: True, pass_bot=True,
        manual=manual_factory.filter())
