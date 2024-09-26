from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from messages.enter import msg_choose_direct, msg_enter_max_bar
from services import calculation, channel_calc, ticker
from config_logger import logger
from db import db
from data.data import liteDb
from Classes import currencyService
from models import Calculation, ForexInfo, UnfinishedCalculation, CallbackQuery, StateContext, User

from states.calculate import CalculateState

from common.calc_step import choose_calculate_step
from common.utils import get_decimal_count, get_lang

from keyboards.settings import kb_first_dep
from keyboards.calculate import (
    calculate_factory, CalculateCallbackFilter,
    kb_calc_cancel, kb_calc_direct
)

from pages.calculate import create_and_send_calc, send_calculation, send_confirm_calc_send, send_main, send_settings


async def _main_callback_handler(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = calculate_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "calculate_factory" user_tg_id={user.tgId} type={type}')

    if type == 'go_main':
        await send_main(bot, call.message, state, user)

    if type == 'calc_back':
        async with state.data() as data:
            last_values = data.get('last_values', [])
            if last_values is not None and len(last_values) > 0:
                value = last_values.pop()
                data[value] = None

        await choose_calculate_step(bot, call.message, state, user, True)

    if type == 'go_settings':
        await send_settings(bot, call.message, state, user)

    if type == 'settings_from_calc' and (await state.get()) is not None:
        async with state.data() as data:
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
            update_risk_rate = updated_risk

            risk_value = is_risk_percent = None
            if risk is not None:
                risk_value = risk[0]
                is_risk_percent = risk[1]

            unfinished_calc = UnfinishedCalculation(
                id=-1,
                user_id=user.id,
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

        await send_settings(bot, call.message, state, user)

    if 'pair' in type:
        _, pair = type.split('+')
        pair_arr = pair.split('/')

        user_settings = db.get_calc_user_settings(user.id)
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

        await state.add_data(
            forex=forex,
        )
        await choose_calculate_step(
            bot, call.message, state, user,
            True, last_value='forex'
        )

    if 'tool' in type:
        _, tool = type.split('++')

        await state.add_data(tool=tool)
        await choose_calculate_step(
            bot, call.message, state, user,
            True, last_value='tool'
        )

    if 'open_price' in type:
        _, open_price_val = type.split('+')

        await state.add_data(
            open_price=float(open_price_val)
        )
        await choose_calculate_step(
            bot, call.message, state, user,
            True, last_value='open_price'
        )

    if 'risk' in type:
        value = float(type.replace('risk', ''))
        await state.add_data(update_risk=value)

        await choose_calculate_step(bot, call.message, state, user, True)

    if type == 'calc_atr':
        await bot.edit_message_text(
            msg_enter_max_bar(user.lang),
            chat_id, mes_id,
            reply_markup=kb_calc_cancel(user.lang)
        )
        await state.set(CalculateState.max_bar)

    if type == 'calc_atr+':
        async with state.data() as data:
            cur_tool: str = data.get('tool', '')
            stop_type: str = data.get('stop_type', '')
            op: float = data.get('open_price', 0)

        atr_settings = liteDb.getUserAtrSettings(user.tgId)
        period, count = atr_settings[1].split('+')

        value = ticker.get_atr(cur_tool, period, int(count))
        if not value:
            return

        rate = 1
        if 'atr_percent' in stop_type:
            _, percent = stop_type.split('+')
            rate = float(percent) * 0.01

        atr = abs(value) * abs(rate)

        await bot.edit_message_text(
            msg_choose_direct(user.lang, user.tgId), chat_id, mes_id,
            reply_markup=kb_calc_direct(user.lang, op, atr)
        )

        await state.add_data(
            atr=atr
        )

    if 'direct+' in type:
        _, action = type.split('+')

        async with state.data() as data:
            atr = data.get('atr', 0)
            stop_loss = data.get('stop_loss')
            stat_id = data.get('stat_id', 0)
            op: float = data.get('open_price', 0)

        if stop_loss == -1:
            stat_id = await create_and_send_calc(
                bot, call.message, state, user,
                stop_loss if action == 'long' else op + 1,
                False
            )
            if not stat_id:
                return

            stat = calculation.get(stat_id)
            if stat is None:
                return

            withoutStop = liteDb.getSendSettings('withoutStop')
            style = liteDb.getSendSettings('style')
            isVote = liteDb.getSendSettings('isVote')
            time = liteDb.getSendSettings('time')

            send_data = channel_calc.create(stat_id)
            if send_data is None:
                return

            if withoutStop == 'True' or stat.stopLoss == -1:
                channel_calc.update(send_data.id, withoutStop=True)
            if isVote == 'False':
                channel_calc.update(send_data.id, isVote=False)
            if style:
                db.change_calculation_style(stat_id, style)
                channel_calc.update(send_data.id, tradingStyle=style)
            if time:
                channel_calc.update(send_data.id, time=time)

            await send_confirm_calc_send(bot, call.message, stat_id)
            await state.delete()
        else:
            atr *= -1 if action == 'long' else 1

            round_c = max(5, get_decimal_count(op))
            stop_loss = round(op + atr, round_c)

            await bot.delete_message(chat_id, mes_id)

            if 'f_direct' in type:
                await state.delete()

                calc = calculation.get(int(stat_id))
                if calc is None:
                    return

                stop_loss = stop_loss if stop_loss is not None else calc.stopLoss

                u_base = db.get_calc_user_settings(user.id, calc.market)

                deposit = risk_val = None
                if u_base is None or u_base.deposit is None:
                    deposit = 10000
                else:
                    deposit = u_base.deposit

                if u_base is not None and u_base.is_from_deposit:
                    count_bet = deposit / calc.openPrice
                    risk_val = count_bet * abs(calc.openPrice - stop_loss)
                else:
                    if u_base is None or u_base.risk is None:
                        risk_val = 100
                    else:
                        risk_val = u_base.risk[0]
                        if u_base.risk[1]:
                            risk_val *= deposit * 0.01

                new_calc = Calculation(
                    id=-1,
                    userId=user.id,
                    currency=calc.currency,
                    deposit=deposit,
                    riskValue=risk_val,
                    market=calc.market,
                    openPrice=calc.openPrice,
                    stopLoss=stop_loss,
                    tradingStyle=calc.tradingStyle,
                    tradingType=calc.tradingType,
                    roundCount=(
                        u_base.round_count or 5) if u_base is not None else 5,
                    tool=calc.tool,
                    tpRatio=calc.tpRatio,
                    splitValues=calc.splitValues,
                    isFromDeposit=u_base.is_from_deposit if u_base is not None else False
                )

                new_id = db.add_calculation(new_calc)
                new_calc.id = new_id or -1

                await send_calculation(bot, call.message, state, user, new_calc, True)
            else:
                await create_and_send_calc(bot, call.message, state, user, stop_loss)

    if type == 'stop_loss':
        await state.add_data(
            stop_type='default'
        )
        await choose_calculate_step(bot, call.message, state, user, True)

    await bot.answer_callback_query(call.id)


async def send_after_first_try(bot: AsyncTeleBot, user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        msg = 'Настройте свой калькулятор, выбрав <b>депозит</b>, <b>процент риска</b>, а все остальное будет рассчитывать система <u>автоматически</u>'
    elif lang == 'uz':
        msg = 'Kalkulyatoringizni <b>depozit</b>, <b>Xavfli</b>, va qolgan barcha narsalar <u>avtomatik</u> ravishda tizimini hisoblab chiqing'
    elif lang == 'tr':
        msg = 'Hesap makinenizi bir <b>depozitosu seçerek ayarlayın</b>, <b>risk yüzdesi</b> ve diğer her şey sistemi <u>otomatik</u> olarak hesaplayacak'
    else:
        msg = 'Set your calculator by choosing a <b>deposit</b>, <b>the percentage of risk</b>, and everything else will calculate the system <u>automatically</u>'

    await bot.send_message(
        user_id, msg,
        reply_markup=kb_first_dep(lang)
    )


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(CalculateCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,  # type: ignore
        lambda _: True, pass_bot=True,
        calculate=calculate_factory.filter()
    )
