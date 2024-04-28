import json
from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db
from common.utils import set_state_data
from Classes import currencyService
from models import ForexInfo, UnfinishedCalculation

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

    if type == 'calc_back':
        with bot.retrieve_data(user_id, chat_id) as data:
            last_values = data.get('last_values')
            if last_values is not None and len(last_values) > 0:
                value = data['last_values'].pop()
                data[value] = None

        choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    if type == 'go_settings':
        send_settings(bot, call.message, user_id)

    if type == 'settings_from_calc' and bot.get_state(user_id, chat_id) is not None:
        with bot.retrieve_data(user_id, chat_id) as data:
            open_price = data.get('open_price')
            tool: str | None = data.get('tool')
            forex: ForexInfo | None = data.get('forex')
            trading_style: str | None = data.get('trading_style')
            risk: tuple[float, bool] | None = data.get('risk')
            updated_risk: float = data.get('updated_risk', 1.)

        if tool is not None or forex is not None:
            user_db_id = db.get_user_id_by_tg_id(user_id)

            risk_value = is_risk_percent = update_risk_rate = None
            if updated_risk and risk is not None:
                update_risk_rate = updated_risk
                risk_value = risk[0]
                is_risk_percent = risk[1]

            unfinished_calc = UnfinishedCalculation(
                id=-1,
                user_id=user_db_id,
                tool=tool,
                forex=forex,
                open_price=open_price,
                trading_style=trading_style,
                risk_value=risk_value,
                is_risk_percent=is_risk_percent,
                update_risk_rate=update_risk_rate,
            )

            db.add_unfinished_calc(unfinished_calc)

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
            choose_calculate_step(
                bot, user_id, chat_id,
                mes_id, True, last_value='forex'
            )

    if 'tool' in type:
        _, tool = type.split('++')

        set_state_data(bot, user_id, chat_id, {'tool': tool})
        choose_calculate_step(
            bot, user_id, chat_id,
            mes_id, True, last_value='tool'
        )

    if 'open_price' in type:
        _, open_price = type.split('+')

        set_state_data(
            bot, user_id, chat_id, {
                'open_price': float(open_price)}
        )
        choose_calculate_step(
            bot, user_id, chat_id, mes_id,
            True, last_value='open_price'
        )

    if 'risk' in type:
        value = float(type.replace('risk', ''))
        with bot.retrieve_data(user_id, chat_id) as data:
            data['updated_risk'] = value

        choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(CalculateCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        calculate=calculate_factory.filter()
    )
