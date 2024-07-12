from telebot import TeleBot
from telebot.types import CallbackQuery

from AuthRoles import get_ticker_atr
from CALCULATE.callbacks.calculate.keyboards import kb_calc_cancel, kb_calc_direct
from CALCULATE.common.messages import msg_choose_direct, msg_enter_max_bar
from CALCULATE.states.calculate import CalculateState
from config_logger import logger
from db import db
from common.utils import delete_message, get_decimal_count, set_state_data
from Classes import currencyService
from models import ForexInfo, UnfinishedCalculation

from .filter import calculate_factory, CalculateCallbackFilter
from ..utils import choose_calculate_step
from ..pages import create_and_send_calc, send_main, send_settings


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = calculate_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "calculate_factory" user_tg_id={user_id} type={type}')

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if type == 'calc_back':
        with bot.retrieve_data(user_id, chat_id) as data:
            last_values = data.get('last_values')
            if last_values is not None and len(last_values) > 0:
                value = data['last_values'].pop()
                data[value] = None

        choose_calculate_step(bot, user_id, call.message, True)

    if type == 'go_settings':
        send_settings(bot, call.message, user_id)

    if type == 'settings_from_calc' and bot.get_state(user_id, chat_id) is not None:
        with bot.retrieve_data(user_id, chat_id) as data:
            open_price: float | None = data.get('open_price')
            tool: str | None = data.get('tool')
            forex: ForexInfo | None = data.get('forex')
            trading_style: str | None = data.get('trading_style')
            risk: tuple[float, bool] | None = data.get('risk')
            updated_risk: float | None = data.get('updated_risk')
            deposit: float | None = data.get('deposit')
            currency: str | None = data.get('currency')
            last_values: list[str] = data.get('last_values') or []

        if tool is not None or forex is not None:
            user_db_id = db.get_user_id_by_tg_id(user_id)
            update_risk_rate = updated_risk

            risk_value = is_risk_percent = None
            if risk is not None:
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
                deposit=deposit,
                currency=currency,
                last_values=last_values
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

        prices = currencyService.getPairsPrice(pairs) or {}

        forex = ForexInfo(
            pair=(pair_arr[0], pair_arr[1]),
            price=prices.get(pair, 1),
            cross_prices=prices
        )

        set_state_data(bot, user_id, chat_id, {
            'forex': forex,
        })
        choose_calculate_step(
            bot, user_id, call.message,
            True, last_value='forex'
        )

    if 'tool' in type:
        _, tool = type.split('++')

        set_state_data(bot, user_id, chat_id, {'tool': tool})
        choose_calculate_step(
            bot, user_id, call.message,
            True, last_value='tool'
        )

    if 'open_price' in type:
        _, open_price_val = type.split('+')

        set_state_data(
            bot, user_id, chat_id, {
                'open_price': float(open_price_val)}
        )
        choose_calculate_step(
            bot, user_id, call.message,
            True, last_value='open_price'
        )

    if 'risk' in type:
        value = float(type.replace('risk', ''))
        with bot.retrieve_data(user_id, chat_id) as data:
            data['updated_risk'] = value

        choose_calculate_step(bot, user_id, call.message, True)

    if type == 'calc_atr':
        bot.edit_message_text(
            msg_enter_max_bar(user_id),
            chat_id, mes_id,
            reply_markup=kb_calc_cancel(user_id)
        )
        bot.set_state(user_id, CalculateState.max_bar, chat_id)

    if type == 'calc_atr+':
        with bot.retrieve_data(user_id, chat_id) as data:
            cur_tool: str = data.get('tool', '')
            stop_type: str = data.get('stop_type', '')

        value = get_ticker_atr(cur_tool)

        bot.edit_message_text(
            msg_choose_direct(user_id), chat_id, mes_id,
            reply_markup=kb_calc_direct(user_id)
        )

        rate = 1
        if 'atr_percent' in stop_type:
            _, percent = stop_type.split('+')
            rate = float(percent) * 0.01

        set_state_data(
            bot, user_id, chat_id, {
                'atr': abs(value) * abs(rate)
            }
        )

    if 'direct+' in type:
        _, action = type.split('+')

        with bot.retrieve_data(user_id, chat_id) as data:
            atr = data.get('atr', 0)
            op: float = data.get('open_price', 0)

        atr *= -1 if action == 'long' else 1

        round_c = get_decimal_count(op)
        stop_loss = round(op + atr, round_c)

        bot.delete_message(chat_id, mes_id)
        create_and_send_calc(bot, call.message, user_id, stop_loss)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(CalculateCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        calculate=calculate_factory.filter()
    )
