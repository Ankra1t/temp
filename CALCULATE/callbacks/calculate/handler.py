from telebot import TeleBot
from telebot.types import CallbackQuery

from services import calculation, channel_calc, ticker
from ..calculate.keyboards import kb_calc_cancel, kb_calc_direct
from ..settings.keyboards import kb_first_dep
from CALCULATE.common.messages import msg_choose_direct, msg_enter_max_bar
from CALCULATE.states.calculate import CalculateState
from config_logger import logger
from db import db
from data.data import liteDb
from common.utils import get_decimal_count, get_lang, set_state_data
from Classes import currencyService
from models import Calculation, ForexInfo, UnfinishedCalculation

from .filter import calculate_factory, CalculateCallbackFilter
from ..utils import choose_calculate_step
from ..pages import create_and_send_calc, send_calculation, send_confirm_calc_send, send_main, send_settings


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

        atr_settings = liteDb.getUserAtrSettings(user_id)
        period, count = atr_settings[1].split('+')

        value = ticker.get_atr(cur_tool, period, int(count))
        if not value:
            return

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
            stop_loss = data.get('stop_loss')
            stat_id = data.get('stat_id')
            op: float = data.get('open_price', 0)

        if stop_loss == -1:
            stat_id = create_and_send_calc(
                bot, call.message, user_id,
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

            send_confirm_calc_send(bot, call.message, stat_id)
            bot.delete_state(user_id, chat_id)
        else:
            atr *= -1 if action == 'long' else 1

            round_c = max(5, get_decimal_count(op))
            stop_loss = round(op + atr, round_c)

            bot.delete_message(chat_id, mes_id)

            if 'f_direct' in type:
                bot.delete_state(user_id, chat_id)

                calc = calculation.get(int(stat_id))
                if calc is None:
                    return

                stop_loss = stop_loss if stop_loss is not None else calc.stopLoss

                user_db_id = db.get_user_id_by_tg_id(user_id)
                u_base = db.get_calc_user_settings(user_db_id, calc.market)

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
                    userId=user_db_id,
                    currency=calc.currency,
                    deposit=deposit,
                    riskValue=risk_val,
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

                send_calculation(bot, call.message, user_id, new_calc, True)
            else:
                create_and_send_calc(bot, call.message, user_id, stop_loss)

    bot.answer_callback_query(call.id)


def send_after_first_try(bot: TeleBot, user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        msg = 'Настройте свой калькулятор, выбрав <b>депозит</b>, <b>процент риска</b>, а все остальное будет рассчитывать система <u>автоматически</u>'
    elif lang == 'uz':
        msg = 'Kalkulyatoringizni <b>depozit</b>, <b>Xavfli</b>, va qolgan barcha narsalar <u>avtomatik</u> ravishda tizimini hisoblab chiqing'
    elif lang == 'tr':
        msg = 'Hesap makinenizi bir <b>depozitosu seçerek ayarlayın</b>, <b>risk yüzdesi</b> ve diğer her şey sistemi <u>otomatik</u> olarak hesaplayacak'
    else:
        msg = 'Set your calculator by choosing a <b>deposit</b>, <b>the percentage of risk</b>, and everything else will calculate the system <u>automatically</u>'

    bot.send_message(
        user_id, msg,
        reply_markup=kb_first_dep(user_id)
    )


def registration(bot: TeleBot):
    bot.add_custom_filter(CalculateCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        calculate=calculate_factory.filter()
    )
