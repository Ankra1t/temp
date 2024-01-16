from telebot import TeleBot
from telebot.types import CallbackQuery

from .filter import main_factory, MainCallbackFilter
from ..utils import choose_first_calculate_step
from ..pages import send_settings, send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = main_factory.parse(call.data)
    type = str(callback_data['type'])

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    calc_types = ('crypto', 'future', 'paper', 'forex')
    if type in calc_types:
        choose_first_calculate_step(bot, user_id, call.message, type, True)

    if type == 'cancel':
        send_main(call.message, bot, user_id)
        bot.clear_step_handler(call.message)
        bot.delete_state(user_id, chat_id)

    if type == 'settings':
        send_settings(bot, call.message, user_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter())
