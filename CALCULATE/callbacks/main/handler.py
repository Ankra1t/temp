from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new

from .filter import main_factory, MainCallbackFilter
from ..utils import choose_first_calculate_step
from ..pages import send_settings, send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id

    if type == 'calc':
        market = db_new.get_calculator_user_market(user_db_id) or 'crypto'
        choose_first_calculate_step(bot, user_id, call.message, market, True)

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
