from telebot import TeleBot
from telebot.types import Message

from CALCULATE.common.messages import msg_choose_direct, msg_enter_atr, msg_enter_stop_loss
from CALCULATE.states.calculate import CalculateState
from common.utils import set_state_data
from data.data import liteDb
from db import db
from MAIN.common.utils import send_in_development

from CALCULATE.callbacks import send_calculation, kb_calc_atr, kb_calc_direct
from MAIN.callbacks import send_user_main, send_admin_main, send_site_code
from models import Calculation
from services import calculation, channel_calc, ticker


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
        send_data = channel_calc.getByCalc(int(id))
        calc = calculation.get(int(id))

        user_db_id = db.get_user_id_by_tg_id(user_id)
        u_base = db.get_calc_user_settings(user_db_id)
        if send_data is None or calc is None or u_base is None:
            return

        if send_data.withoutStop and not has_registered_now:
            stop_type = liteDb.getUserStop(user_id) or ''

            if 'atr' in stop_type:
                atr_settings = liteDb.getUserAtrSettings(user_id)
                period, count = atr_settings[1].split('+')

                bot.set_state(user_id, CalculateState.stop_atr, chat_id)

                ticker_val = ticker.get_atr(
                    calc.tool or '', period, int(count)) or None

                if atr_settings[0] and ticker_val is not None:
                    rate = 1
                    if 'atr_percent' in stop_type:
                        _, percent = stop_type.split('+')
                        rate = float(percent) * 0.01

                    set_state_data(
                        bot, user_id, chat_id, {
                            'atr': abs(ticker_val) * abs(rate)
                        }
                    )
                    bot.send_message(
                        chat_id, msg_choose_direct(user_id, ticker_val),
                        reply_markup=kb_calc_direct(user_id, True)
                    )
                else:
                    bot.send_message(
                        chat_id, msg_enter_atr(user_id, calc),
                        reply_markup=kb_calc_atr(user_id, ticker_val)
                    )
            else:
                bot.send_message(
                    chat_id, msg_enter_stop_loss(user_id, send_stat=calc),
                )
                bot.set_state(user_id, CalculateState.stop_loss, chat_id)

            set_state_data(
                bot, user_id, chat_id,
                {
                    'action': 'send_calc',
                    'stat_id': id,
                    'open_price': calc.openPrice,
                    'tool': calc.tool,
                    'deposit': u_base.deposit,
                    'risk': u_base.risk
                }
            )
        else:
            start_with_calc(bot, message, user_id, int(id), is_try=has_registered_now)

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


def start_with_calc(
    bot: TeleBot,
    message: Message,
    user_id: int,
    stat_id: int,
    stop_loss: float | None = None,
    is_try=False
):
    chat_id = message.chat.id

    bot.delete_state(user_id, chat_id)

    calc = calculation.get(int(stat_id))
    if calc is None:
        return

    stop_loss = stop_loss if stop_loss is not None else calc.stopLoss

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id, calc.market)

    deposit = risk = None
    if u_base is None or u_base.deposit is None:
        deposit = 1000
    else:
        deposit = u_base.deposit

    if u_base is not None and u_base.is_from_deposit:
        count_bet = deposit / calc.openPrice
        risk = count_bet * abs(calc.openPrice - stop_loss)
    else:
        if u_base is None or u_base.risk is None:
            risk = 10
        else:
            risk = u_base.risk[0]
            if u_base.risk[1]:
                risk *= deposit * 0.01

    new_calc = Calculation(
        id=-1,
        userId=user_db_id,
        currency=calc.currency,
        deposit=deposit,
        riskValue=risk,
        market=calc.market,
        openPrice=calc.openPrice,
        stopLoss=stop_loss,
        tradingStyle=calc.tradingStyle,
        tradingType=calc.tradingType,
        roundCount=(u_base.round_count or 5) if u_base is not None else 5,
        tool=calc.tool,
        tpRatio=calc.tpRatio,
        splitValues=calc.splitValues,
        isFromDeposit=u_base.is_from_deposit if u_base is not None else False
    )

    new_id = db.add_calculation(new_calc)
    new_calc.id = new_id or -1
    send_calculation(bot, message, user_id, new_calc, True, is_try=is_try)
