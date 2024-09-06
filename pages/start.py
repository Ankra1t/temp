from telebot.async_telebot import AsyncTeleBot

from data.data import liteDb
from db import db

from common.utils import send_in_development

from states.calculate import CalculateState
from messages.enter import msg_choose_direct, msg_enter_atr, msg_enter_stop_loss

from pages.calculate import send_calculation
from pages.user import send_user_main, send_site_code
from pages.admin import send_admin_main

from keyboards.calculate import kb_calc_atr, kb_calc_direct

from models import Calculation, Message, StateContext, User
from services import calculation, channel_calc, ticker


async def send_start_by_user(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    has_registered_now=False
):
    chat_id = message.chat.id

    await state.delete()

    if message.text is not None and len(message.text.split()) == 2 and 'calc' in message.text:
        _, id = message.text.split('_')
        send_data = channel_calc.getByCalc(int(id))
        calc = calculation.get(int(id))

        u_base = db.get_calc_user_settings(user.id)
        if send_data is None or calc is None or u_base is None:
            return

        if send_data.withoutStop and not has_registered_now:
            stop_type = liteDb.getUserStop(user.tgId) or ''

            if 'atr' in stop_type:
                atr_settings = liteDb.getUserAtrSettings(user.tgId)
                period, count = atr_settings[1].split('+')

                await state.set(CalculateState.stop_atr)

                ticker_val = ticker.get_atr(
                    calc.tool or '', period, int(count)) or None

                if atr_settings[0] and ticker_val is not None:
                    rate = 1
                    if 'atr_percent' in stop_type:
                        _, percent = stop_type.split('+')
                        rate = float(percent) * 0.01
                    await bot.add_data(
                        chat_id=chat_id,
                        user_id=user.tgId,
                        atr=abs(ticker_val) * abs(rate)
                    )
                    await bot.send_message(
                        chat_id, msg_choose_direct(user.lang, ticker_val),
                        reply_markup=kb_calc_direct(user.lang, True)
                    )
                else:
                    await bot.send_message(
                        chat_id, msg_enter_atr(user.lang, calc),
                        reply_markup=kb_calc_atr(user.lang, user.tgId, ticker_val)
                    )
            else:
                await bot.send_message(
                    chat_id, msg_enter_stop_loss(user.lang, send_stat=calc),
                )
                await state.set(CalculateState.stop_loss)

            await bot.add_data(
                chat_id=chat_id,
                user_id=user.tgId,
                action='send_calc',
                stat_id=id,
                open_price=calc.openPrice,
                tool=calc.tool,
                deposit=u_base.deposit,
                risk=u_base.risk
            )
        else:
            await start_with_calc(
                bot, message, user.tgId, int(id),
                is_try=has_registered_now
            )

    elif user.role == 0:
        await send_user_main(bot, message, state, user, has_registered_now, True)

    elif message.text is not None and len(message.text.split()) == 2:
        _, code = message.text.split()
        if code == 'site':
            await send_site_code(bot, message, state, user, is_first=True)
            return

    elif user.role == 1:
        await send_admin_main(bot, message, state, True)

    elif user.role in (2, 3):
        await send_in_development(bot, message)


async def start_with_calc(
    bot: AsyncTeleBot,
    message: Message,
    user_id: int,
    stat_id: int,
    stop_loss: float | None = None,
    is_try=False
):
    chat_id = message.chat.id

    await bot.delete_state(user_id, chat_id)

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
    await send_calculation(bot, message, user_id, new_calc, True, is_try=is_try)
