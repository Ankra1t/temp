from telebot import TeleBot
from telebot.types import Message

from CALCULATE.common.messages import msg_enter_stop_loss
from CALCULATE.states.calculate import CalculateState
from common.utils import set_state_data
from data.data import liteDb
from db import db
from MAIN.common.utils import send_in_development

from CALCULATE.callbacks import send_calculation
from MAIN.callbacks import send_user_main, send_admin_main, send_site_code
from models import Calculation


def send_start_by_user(
    bot: TeleBot,
    message: Message,
    user_id: int,
    user_role: int,
    has_registered_now=False
):
    chat_id = message.chat.id
    bot.delete_state(user_id, chat_id)

    if message.text is not None and len(message.text.split()) == 2 and 'calc' in message.text:
        _, id = message.text.split('_')
        send_data = liteDb.getSendCalc(int(id))
        calc = db.get_calculation(int(id))
        if send_data is None or calc is None:
            return

        if send_data.without_stop:
            bot.send_message(
                chat_id, msg_enter_stop_loss(user_id, send_stat=calc),
            )
            bot.set_state(user_id, CalculateState.stop_loss, chat_id)
            set_state_data(
                bot, user_id, chat_id,
                {
                    'action': 'send_calc',
                    'stat_id': id,
                    'open_price': calc.open_price,
                }
            )
        else:
            start_with_calc(bot, message, user_id, int(id))

    elif user_role == 0:
        send_user_main(bot, message, user_id, True, has_registered_now)

    elif message.text is not None and len(message.text.split()) == 2:
        _, code = message.text.split()
        if code == 'site':
            send_site_code(bot, message, user_id, True)
            return

    elif user_role == 1:
        send_admin_main(bot, message, user_id, True)

    elif user_role in (2, 3):
        send_in_development(bot, message)


def start_with_calc(bot: TeleBot, message: Message, user_id: int, stat_id: int, stop_loss: float | None = None):
    chat_id = message.chat.id

    bot.delete_state(user_id, chat_id)

    calc = db.get_calculation(int(stat_id))
    if calc is None:
        return

    stop_loss = stop_loss if stop_loss is not None else calc.stop_loss

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id, calc.market)

    deposit = risk = None
    if u_base is None or u_base.deposit is None:
        deposit = 10000
    else:
        deposit = u_base.deposit

    if u_base is not None and u_base.is_from_deposit:
        count_bet = deposit / calc.open_price
        risk = count_bet * abs(calc.open_price - stop_loss)
    else:
        if u_base is None or u_base.risk is None:
            risk = 100
        else:
            risk = u_base.risk[0]
            if u_base.risk[1]:
                risk *= deposit * 0.01

    new_calc = Calculation(
        id=-1,
        user_id=user_db_id,
        currency=calc.currency,
        deposit=deposit,
        risk_value=risk,
        market=calc.market,
        open_price=calc.open_price,
        stop_loss=stop_loss,
        trading_style=calc.trading_style,
        trading_type=calc.trading_type,
        round_count=(u_base.round_count or 5) if u_base is not None else 5,
        tool=calc.tool,
        tp_ratio=calc.tp_ratio,
        split_values=calc.split_values,
        is_from_deposit=u_base.is_from_deposit if u_base is not None else False
    )

    new_id = db.add_calculation(new_calc)
    new_calc.id = new_id or -1

    send_calculation(bot, message, user_id, new_calc, True)
