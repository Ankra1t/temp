from telebot import TeleBot
from telebot.types import Message

from CALCULATE.states.calculate import CalculateState
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
        if not liteDb.checkSendCalc(int(id)):
            return

        bot.set_state(user_id, CalculateState.tool, chat_id)

        calc = db.get_calculation(int(id))
        if calc is None:
            return

        user_db_id = db.get_user_id_by_tg_id(user_id)
        u_base = db.get_calc_user_settings(user_db_id, calc.market)

        deposit = risk = None
        if u_base is None or u_base.deposit is None:
            deposit = 10000
        else:
            deposit = u_base.deposit

        if u_base is None or u_base.risk is None:
            risk = 100
        else:
            risk = u_base.risk[0]
            if u_base.risk[1]:
                risk *= deposit * 0.01

        new_calc = Calculation(
            id=-1,
            user_id=user_id,
            currency=calc.currency,
            deposit=deposit,
            risk_value=risk,
            market=calc.market,
            open_price=calc.open_price,
            stop_loss=calc.stop_loss,
            trading_style=calc.trading_style,
            trading_type=calc.trading_type,
            round_count=(u_base.round_count or 5) if u_base is not None else 5,
            tool=calc.tool,
            tp_ratio=calc.tp_ratio,
            split_values=calc.split_values
        )

        new_id = db.add_calculation(new_calc)
        new_calc.id = new_id or -1

        send_calculation(bot, message, user_id, new_calc, True)

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
