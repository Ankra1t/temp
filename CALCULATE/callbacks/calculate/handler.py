from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db
from common.utils import set_state_data
from Classes import currencyService
from models import ForexInfo

from .filter import calculate_factory, CalculateCallbackFilter
from ..utils import choose_calculate_step
from ..pages import send_main, send_settings


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = calculate_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if type == 'go_settings':
        send_settings(bot, call.message, user_id)

    if 'pair' in type:
        _, pair = type.split('+')
        pair_arr = pair.split('/')

        user_db_id = db.get_user_id_by_tg_id(user_id)
        user_settings = db.get_calc_user_settings(user_db_id)
        user_currency = getattr(user_settings, 'currency') or 'USD'

        price = currencyService.getPrice(pair_arr[0], pair_arr[1])
        pairs = [pair]
        if user_currency not in pair:
            pairs.append(f'{user_currency}/{pair_arr[1]}')
            pairs.append(f'{pair_arr[0]}/{user_currency}')

        prices = currencyService.getPairsPrice(pairs)

        if prices != False:
            forex = ForexInfo(
                pair=(pair_arr[0], pair_arr[1]),
                price=prices.get(pair, 1),
                cross_prices=prices
            )

            set_state_data(bot, user_id, chat_id, {
                'forex': forex,
            })
            choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    if 'tool' in type:
        _, tool = type.split('++')

        set_state_data(bot, user_id, chat_id, {'tool': tool})
        choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    if 'open_price' in type:
        _, open_price = type.split('+')

        set_state_data(bot, user_id, chat_id, {'open_price': float(open_price)})
        choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(CalculateCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        calculate=calculate_factory.filter()
    )
