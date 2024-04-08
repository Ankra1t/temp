from telebot import TeleBot
from telebot.types import CallbackQuery

from common.utils import set_state_data
from initialize import currencyService
from db import db
from models import ForexInfo

from .filter import calculate_factory, CalculateCallbackFilter
from ..utils import choose_calculate_step
from ..pages import send_main


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = calculate_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if 'pair' in type:
        _, pair = type.split('+')
        pair_arr = pair.split('/')

        price = currencyService.getPrice(pair_arr[0], pair_arr[1])
        if price != False:
            forex = ForexInfo(
                pair=(pair_arr[0], pair_arr[1]),
                price=price,
                cross_prices={}
            )

            set_state_data(bot, user_id, chat_id, {
                'forex': forex,
            })
            choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(CalculateCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        calculate=calculate_factory.filter()
    )
