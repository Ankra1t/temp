from telebot.async_telebot import AsyncTeleBot

from service import user_settings_storage

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
    has_registered_now=False,
    quick_calc_tool: str | None = None,
    quick_calc_price: float | None = None,
):
    chat_id = message.chat.id

    await state.delete()

    # Обработка быстрого запуска калькулятора из start параметра
    if quick_calc_tool is not None and quick_calc_price is not None:
        await _start_quick_calc(
            bot, message, state, user,
            quick_calc_tool, quick_calc_price
        )
        return

    if message.text is not None and len(message.text.split()) == 2 and 'calc' in message.text:
        _, id = message.text.split('_')
        send_data = channel_calc.getByCalc(int(id))
        calc = calculation.get(userId=user.id, calcId=int(id))

        u_base = user_settings_storage.get_or_create(user.tgId)
        if send_data is None or calc is None or u_base is None:
            return

        if send_data.withoutStop and not has_registered_now:
            stop_type = user_settings_storage.get_user_stop(user.tgId) or ''

            if 'atr' in stop_type:
                atr_settings = user_settings_storage.get_user_atr_settings(
                    user.tgId)
                period, count = atr_settings[1].split('+')

                await state.set(CalculateState.stop_atr)

                ticker_val = ticker.get_atr(
                    calc.tool or '', period, int(count)
                ) or None

                if atr_settings[0] and ticker_val is not None:
                    rate = 1
                    if 'atr_percent' in stop_type:
                        _, percent = stop_type.split('+')
                        rate = float(percent) * 0.01

                    atr = abs(ticker_val) * abs(rate)
                    await state.add_data(
                        atr=atr
                    )
                    await bot.send_message(
                        chat_id,
                        msg_choose_direct(user.lang, user.tgId, ticker_val),
                        reply_markup=kb_calc_direct(user.lang, atr, True)
                    )
                else:
                    await bot.send_message(
                        chat_id, msg_enter_atr(user.lang, calc),
                        reply_markup=kb_calc_atr(
                            user.lang, user.tgId, ticker_val)
                    )
            else:
                await bot.send_message(
                    chat_id, msg_enter_stop_loss(user.lang, send_stat=calc),
                )
                await state.set(CalculateState.stop_loss)

            await state.add_data(
                action='send_calc',
                stat_id=id,
                open_price=calc.openPrice,
                tool=calc.tool,
                deposit=u_base.deposit,
                risk=u_base.risk
            )
        elif has_registered_now:
            await first_start_with_calc(
                bot, message, state, user
            )
        else:
            await start_with_calc(
                bot, message, state, user, int(id),
            )

    elif message.text is not None and len(message.text.split()) == 2 and 'site' in message.text:
        await send_site_code(bot, message, state, user, is_first=True)
        return

    elif user.role == 0:
        await send_user_main(bot, message, state, user, has_registered_now, True)

    elif user.role == 1:
        await send_admin_main(bot, message, state, True)

    elif user.role in (2, 3):
        await send_in_development(bot, message)


async def start_with_calc(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    stat_id: int,
    stop_loss: float | None = None,
):
    await state.delete()

    calc = calculation.get(userId=user.id, calcId=int(stat_id))
    if calc is None:
        return

    stop_loss = stop_loss if stop_loss is not None else calc.stopLoss

    u_base = user_settings_storage.get_or_create(user.tgId)

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
        userId=user.id,
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
        isFromDeposit=u_base.is_from_deposit if u_base is not None else False,
        newStop=calc.newStop
    )

    # TODO: Добавить создание расчёта через API
    # new_id = db.add_calculation(new_calc)
    # new_calc.id = new_id or -1
    new_calc.id = -1
    await send_calculation(bot, message, state, user, new_calc, True)


async def first_start_with_calc(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
):
    new_calc = Calculation(
        id=-1,
        userId=user.id,
        currency='USDT',
        deposit=10000,
        riskValue=100,
        market='crypto',
        openPrice=62000,
        stopLoss=61500,
        tradingStyle=None,
        tradingType='margin',
        roundCount=None,
        tool='BTC/USDT',
        tpRatio=[3, 4, 5],
        splitValues=None,
        isFromDeposit=False,
    )

    await send_calculation(bot, message, state, user, new_calc, is_try=True)


async def _start_quick_calc(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    tool: str,
    open_price: float,
):
    """Запуск калькулятора с предустановленными tool и openPrice"""
    u_base = user_settings_storage.get_or_create(user.tgId)

    tool = tool.replace('USDT', '').replace('/', '') + '/USDT'

    await state.set(CalculateState.stop_loss)

    await state.add_data(
        tool=tool,
        open_price=open_price,
        deposit=u_base.deposit if u_base else 10000,
        risk=u_base.risk if u_base else (100, False),
        currency=u_base.currency if u_base else 'USDT',
        trading_type=u_base.trading_type if u_base else 'margin',
        calc_type='crypto',
        stop_type='default',
        stop_loss=-1,
    )

    await bot.send_message(
        message.chat.id,
        f'<b>{tool}</b>\nЦена входа: <code>{open_price}</code>$ \n' +
        msg_enter_stop_loss(user.lang)
    )
