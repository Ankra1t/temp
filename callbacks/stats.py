import os
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from states.admin_params import AdminParamsState
from states.calculate import CalculateState, ForexCalcState
from states.stats import ChannelCalcState, StatsState

from common.utils import delete_message, edit_message

from config_logger import logger

from db import db
from models import MARKETS_TYPE, CallbackQuery, StateContext, User
from services import calculation, channel_calc

# TODO - months в common файл
from messages.calc import msg_calculate_change, msg_calculate_delete, msg_calculation, msg_calculation_deleted
from messages.enter import msg_enter_auto_take, msg_enter_calc_img_text, msg_enter_cancel_at, msg_enter_deposit, msg_enter_new_stop, msg_enter_open_price, msg_enter_pair, msg_enter_profit_minus, msg_enter_profit_sum, msg_enter_risk_percent, msg_enter_save_calc, msg_enter_stop_loss, msg_enter_take_price, msg_enter_tool, msg_enter_tr_stop, msg_enter_trading_style

from keyboards.settings import kb_take_profit, kb_trading_style
from keyboards.channel_post import kb_channel_calc_result_stop, kb_channel_calc_result_take
from keyboards.main import kb_main
from keyboards.stats import (
    kb_auto_take, kb_calc_back, kb_cancel_at, kb_channel_confirm_back, kb_channel_item_back, kb_channel_trailing_stop, stats_factory, StatsCallbackFilter,
    kb_calc_image_text, kb_calc_result, kb_calculate_change,
    kb_calculate_delete, kb_deal_profit_cancel,
    kb_deal_profit_minus, kb_deal_result, kb_send_calc_time
)
from pages.calculate import create_and_send_channel_calc, send_admin_channel_calc_item, send_calc_list, send_calculation, send_confirm_calc_send, send_main, send_stats


async def _main_callback_handler(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = stats_factory.parse(call.data)
    type = callback_data.get('type', '')
    calc_id = int(callback_data.get('stat_id', 0))
    page = int(callback_data.get('p', 0))
    stats_market: MARKETS_TYPE = callback_data.get(
        'sm', 'crypto'
    )  # type: ignore

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "stats_factory" user_tg_id={user.tgId} type={type} ({stats_market} {calc_id})'
    )

    if type == 'get_calc':
        await bot.edit_message_reply_markup(chat_id, mes_id, reply_markup=None)

        calc = calculation.get(userId=user.id, calcId=calc_id)

        if calc:
            await send_calculation(bot, call.message, state, user, calc, True)

    if 'profit' in type:
        await state.delete()
        _, profit = type.split('+')

        if profit == '':
            await delete_message(bot, chat_id, mes_id)
            await bot.send_message(
                chat_id, msg_enter_save_calc(user.lang),
                reply_markup=kb_deal_result(user.lang, calc_id)
            )
        else:
            is_cancel = False

            calc_info = calculation.get(userId=user.id, calcId=calc_id)
            if calc_info is None:
                return

            send_data = channel_calc.getByCalc(calc_id)

            if calc_info.ActiveCalc is not None and send_data is None:
                return

            if profit == '-':
                await state.set(StatsState.loss)
                await state.add_data(stat_id=calc_id)
                await bot.edit_message_text(
                    msg_enter_profit_minus(user.lang),
                    chat_id, mes_id,
                    reply_markup=kb_deal_profit_minus(user.lang, calc_id)
                )
            else:
                if 'loss' in profit:
                    # TODO - Проверить, зачем выставлять результат отсюда
                    pass
                    # rate = float(profit.replace('loss', ''))
                    # _, _, spot_rate = get_count_value_bet(calc_info)
                    # calcService.set_profit(
                    #     user.tgId,
                    #     calc_id, -calc_info.riskValue * rate * spot_rate
                    # )
                elif profit != 'cancel':
                    # TODO - Проверить, зачем выставлять результат отсюда
                    pass
                    # _, _, spot_rate = get_count_value_bet(calc_info)
                    # profit_result = calc_info.riskValue * \
                    #     int(profit) * spot_rate
                    # calcService.set_profit(
                    #     user.tgId,
                    #     calc_id, profit_result
                    # )
                else:
                    is_cancel = True

                calc_info = calculation.get(userId=user.id, calcId=calc_id)
                if calc_info is None:
                    return

                await send_calculation(bot, call.message, state, user, calc_info)

                if not is_cancel:
                    calculation.update(
                        userId=user.id, calcId=calc_id, status='FINISH'
                    )

    if type == 'sum':
        await state.set(StatsState.sum)
        await state.add_data(stat_id=calc_id)
        await bot.edit_message_text(
            msg_enter_profit_sum(user.lang),
            chat_id, mes_id,
            reply_markup=kb_deal_profit_cancel(user.lang, calc_id)
        )

    if type == 'go_main':
        await send_main(bot, call.message, state, user)

    if type == 'go_stats':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is not None and not calc.openedList:
            try:
                await bot.edit_message_reply_markup(
                    chat_id, mes_id,
                    reply_markup=kb_calc_result(user.lang, calc)
                )
            except:
                pass

        await send_stats(
            bot, call.message, state, user,
            calc is not None and not calc.openedList
        )

    if type == 'stats_market':
        # stats = calcService.get_stats(user.tgId, stats_market)
        # text = msg_market_stats(user.lang, stats_market, stats)

        # await bot.edit_message_text(
        #     text, chat_id, mes_id,
        #     reply_markup=ww(user.lang, 'market')
        # )
        await bot.send_message(
            chat_id, 'В разработке'
        )

    if type == 'back_calc' or type == 'refresh':
        calc = calculation.get(userId=user.id, calcId=calc_id)

        if calc is not None:
            if type != 'refresh' or calc.status != 'WAIT':
                try:
                    await send_calculation(bot, call.message, state, user, calc)
                except:
                    pass

    if type == 'result_calc':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is not None:
            await bot.edit_message_reply_markup(
                chat_id, mes_id,
                reply_markup=kb_calc_result(user.lang, calc, True)
            )

    if 'delete_calc' in type:
        if '_yes' in type:
            if db.delete_calculation(calc_id):
                await edit_message(
                    bot, call.message, 'text',
                    msg_calculation_deleted(user.lang),
                )
                await send_main(bot, call.message, state, user, True)
        elif '_no' in type:
            prev_type = call.message.content_type

            if prev_type == 'text':
                text = call.message.html_text or 'err\n'
            else:
                text = call.message.html_caption or 'err\n'

            text = '\n'.join(text.split('\n')[:-1])
            media = call.message.photo[-1].file_id if call.message.photo else None

            calc_info = calculation.get(userId=user.id, calcId=calc_id)

            await edit_message(
                bot, call.message, prev_type,  # type: ignore
                text,
                kb_main(user.lang, user.tgId, calc_info),
                media
            )
        else:
            prev_type = call.message.content_type

            if prev_type == 'text':
                text = call.message.html_text or 'err\n'
            else:
                text = call.message.html_caption or 'err\n'

            media = call.message.photo[-1].file_id if call.message.photo else None

            await edit_message(
                bot, call.message, prev_type,  # type: ignore
                msg_calculate_delete(user.lang, text),
                kb_calculate_delete(user.lang, calc_id),
                media
            )

    if 'ch_c' in type:
        calc_info = calculation.get(userId=user.id, calcId=calc_id)
        type_arr = type.split('+')
        kind = ''

        if len(type_arr) == 2:
            kind = type_arr[1]

        if kind == '':
            prev_type = call.message.content_type

            if prev_type == 'text':
                text = call.message.html_text or 'err\n'
            else:
                text = call.message.html_caption or 'err\n'

            media = call.message.photo[-1].file_id if call.message.photo else None

            if calc_info:
                await edit_message(
                    bot, call.message, prev_type,  # type: ignore
                    msg_calculate_change(user.lang, text),
                    kb_calculate_change(user.lang, calc_info),
                    media
                )
        elif kind == 'back':
            prev_type = call.message.content_type

            if prev_type == 'text':
                text = call.message.html_text or 'err\n'
            else:
                text = call.message.html_caption or 'err\n'

            text = '\n'.join(text.split('\n')[:-1])
            media = call.message.photo[-1].file_id if call.message.photo else None

            await edit_message(
                bot, call.message, prev_type,  # type: ignore
                text,
                kb_main(user.lang, user.tgId, calc_info),
                media
            )
        elif kind == 'open_price':
            await edit_message(
                bot, call.message, 'text',
                msg_enter_open_price(user.lang),
                kb_deal_profit_cancel(user.lang, calc_id)
            )
            await state.set(CalculateState.open_price)
            await state.add_data(
                stat_id=calc_id,
                del_mes_id=call.message.id
            )
        elif kind == 'stop_loss':
            await edit_message(
                bot, call.message, 'text',
                msg_enter_stop_loss(user.lang),
                kb_deal_profit_cancel(user.lang, calc_id)
            )
            await state.set(CalculateState.stop_loss)
            await state.add_data(
                stat_id=calc_id,
                del_mes_id=call.message.id
            )
        elif kind == 'tool':
            calc = calculation.get(userId=user.id, calcId=calc_id)
            if calc is None or calc.ActiveCalc:
                return

            if calc.forexInfo is not None:
                new_state = ForexCalcState.pair
                msg = msg_enter_pair(user.lang)
            else:
                new_state = CalculateState.tool
                msg = msg_enter_tool(user.lang, calc.market)

            await edit_message(
                bot, call.message, 'text', msg,
                kb_deal_profit_cancel(user.lang, calc_id)
            )
            await state.set(new_state)
            await state.add_data(
                stat_id=calc_id,
                del_mes_id=call.message.id
            )
        elif kind == 'dep':
            await edit_message(
                bot, call.message, 'text',
                msg_enter_deposit(user.lang),
                kb_deal_profit_cancel(user.lang, calc_id)
            )
            await state.set(CalculateState.deposit)
            await state.add_data(
                stat_id=calc_id,
                del_mes_id=call.message.id,
                calc_id=calc_id,
            )
        elif kind == 'risk':
            await edit_message(
                bot, call.message, 'text',
                msg_enter_risk_percent(user.lang),
                kb_deal_profit_cancel(user.lang, calc_id)
            )
            await state.set(CalculateState.risk_percent)
            await state.add_data(
                stat_id=calc_id,
                del_mes_id=call.message.id,
                calc_id=calc_id,
            )
        elif 'style' in kind:
            stc = '+stc' if '_stc' in type else ''
            await edit_message(
                bot, call.message, 'text',
                msg_enter_trading_style(user.lang),
                kb_trading_style(user.lang, 'ch_calc' + stc)
            )
            await state.set(CalculateState.trading_style)
            await state.add_data(
                stat_id=calc_id,
                del_mes_id=call.message.id
            )
        elif 'take' in kind:
            calc = calculation.get(userId=user.id, calcId=calc_id)

            if calc:
                await bot.edit_message_text(
                    msg_calculation(user.lang, calc),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(
                        user.lang, calc.tpRatio, calc.id
                    )
                )

    if 'tp_rate+' in type:
        _, rate = type.split('+')
        rate = int(rate)

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc and len(calc.tpRatio) != 1:
            if rate in calc.tpRatio:
                calc.tpRatio.remove(rate)
            else:
                calc.tpRatio.append(rate)
                calc.tpRatio.sort()

            calc = calculation.update(
                userId=user.id, calcId=calc.id, tpRatio=calc.tpRatio)
            if calc:
                await bot.edit_message_text(
                    msg_calculation(user.lang, calc),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(
                        user.lang, calc.tpRatio, calc.id)
                )

    if 'del_img_txt' in type:
        calc = calculation.update(
            userId=user.id, calcId=calc_id, photo=None, description=None)
        if calc is None:
            return

        if 'stc+' in type:
            await send_confirm_calc_send(bot, call.message, calc_id)
        else:
            await send_calculation(bot, call.message, state, user, calc)

    if 'add_img_text' in type:
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None:
            return

        text = msg_enter_calc_img_text(user.lang, calc)
        kb = kb_calc_image_text(
            user.lang, calc, 'stc+' if 'stc+' in type else '')

        new_mes_id = await edit_message(bot, call.message, 'text', text, kb)

        await state.set(StatsState.add_image_text)
        await state.add_data(
            stat_id=calc_id,
            calc_text=text,
            del_mes_id=new_mes_id,
            type='stc' if 'stc+' in type else ''
        )

    if type == 'comment':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc is None:
            return

        text = 'Введите комментарий:'
        kb = kb_calc_image_text(user.lang, calc)

        new_mes_id = await edit_message(bot, call.message, 'text', text, kb)

        await state.set(StatsState.add_image_text)
        await state.add_data(
            stat_id=calc_id,
            type='stats',
            del_mes_id=new_mes_id,
        )

    if type == 'send_to_channels':
        await create_and_send_channel_calc(bot, call.message, calc_id, mes_id, user)

    if type == 'stc+send':
        send_data = channel_calc.getByCalc(calc_id)
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if send_data is None or calc is None:
            return

        if send_data.isVote:
            new_mes = await bot.send_message(
                chat_id, f'Опрос будет отправлен через {5} секунд'
            )

        await bot.delete_message(chat_id, mes_id)
        # await bot.send_message(chat_id, '✅ Отправлено')
        await send_main(bot, call.message, state, user, True)

    if type == 'stc+time':
        await edit_message(
            bot, call.message, 'text',
            '👉 Выберите тип периода:',
            kb_send_calc_time(calc_id)
        )

    if 'stc+time=' in type:
        send_data = channel_calc.getByCalc(calc_id)
        if send_data is None:
            return

        _, value = type.split('=')
        value = None if value == 'none' else value

        channel_calc.update(send_data.id, time=value)
        await send_confirm_calc_send(bot, call.message, calc_id)

    if type == 'stc+stop':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        send_data = channel_calc.getByCalc(calc_id)
        if send_data is None or calc is None or calc.stopLoss == -1:
            return

        channel_calc.update(
            send_data.id, withoutStop=not send_data.withoutStop
        )
        await send_confirm_calc_send(bot, call.message, calc_id)

    if type == 'stc+vote':
        send_data = channel_calc.getByCalc(calc_id)
        if send_data is None:
            return

        channel_calc.update(send_data.id, isVote=not send_data.isVote)
        await send_confirm_calc_send(bot, call.message, calc_id)

    if type == 'stc+back':
        await send_confirm_calc_send(bot, call.message, calc_id)

    if type == 'ch_tr_stop':
        await edit_message(
            bot, call.message, 'text',
            '👉 Введите значение для скользящего стопа',
            kb_channel_trailing_stop(user.lang, calc_id, True)
        )
        await state.set(AdminParamsState.trailing_stop)
        await state.add_data(
            del_mes_id=mes_id,
            calc_id=calc_id
        )

    if 'ch_tr_stop+' in type:
        _, value = type.split('+')

        if value == '0':
            value = None
        else:
            value = float(value)

        calculation.updateActive(
            userId=user.id, id=calc_id,
            trailingStopCount=value,
            autoTake=None
        )

        await send_confirm_calc_send(bot, call.message, calc_id)

    if type == 'result_cancel':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc and not (calc.ActiveCalc and calc.status == 'WAIT'):
            calc = calculation.update(
                userId=user.id, calcId=calc_id, status='CANCEL'
            )

            if calc is None:
                return

        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'result_deal':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc and not calc.ActiveCalc:
            calc = calculation.update(
                userId=user.id, calcId=calc_id, status='DEAL'
            )

        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'result_wait':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc and not calc.ActiveCalc:
            calc = calculation.update(
                userId=user.id, calcId=calc_id, status='WAIT'
            )
            if calc is None:
                return

        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'result_take':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        send_data = channel_calc.getByCalc(calc_id)
        if calc and not (calc.ActiveCalc and not send_data):
            await bot.edit_message_reply_markup(
                chat_id, mes_id, reply_markup=kb_channel_calc_result_take(
                    calc.tpRatio, calc_id, True
                )
            )
            await state.set(ChannelCalcState.loss)
            await state.add_data(
                del_mes_id=mes_id,
                stat_id=calc_id,
                is_calc=True,
                type='take'
            )

    if type == 'result_stop':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        send_data = channel_calc.getByCalc(calc_id)
        if calc and not (calc.ActiveCalc and not send_data):
            await bot.edit_message_reply_markup(
                chat_id, mes_id, reply_markup=kb_channel_calc_result_stop(
                    calc_id, True
                )
            )
            await state.set(ChannelCalcState.loss)
            await state.add_data(
                del_mes_id=mes_id,
                stat_id=calc_id,
                is_calc=True,
                type='stop'
            )

    if 'list+' in type:
        _, list_type = type.split('+')
        await send_calc_list(bot, call.message, state, user, list_type, page)

    if type == 'active_calc_a':
        calculation.activate(userId=user.id, id=calc_id)
        calc = calculation.get(userId=user.id, calcId=calc_id)

        if calc and calc.ActiveCalc:
            if calc.photo:
                file_id = calc.photo
                file = await bot.get_file(file_id)
                file_bytes = await bot.download_file(file.file_path)

                name = f'{file_id}.png'
                with open(name, 'wb') as new_file:
                    new_file.write(file_bytes)

                with open(name, 'rb') as file:
                    data = calculation.sendPhoto(userId=user.id, file=file)

                os.remove(name)

            type = 'active_calc'

    if type == 'active_calc':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc:
            await send_calculation(
                bot, call.message, state, user, calc, is_activate=True
            )

    if type == 'cancel_at' or type == 'stc_cancel_at':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            msg_enter_cancel_at(user.lang, True),
            kb_cancel_at(user.lang, calc_id, 'stc_' if 'stc_' in type else '')
        )
        await state.set(StatsState.cancel_at)
        await state.add_data(
            calc_id=calc_id,
            del_mes_id=new_mes_id,
            action='stc' if 'stc_' in type else ''
        )

    if 'cancel_at+' in type:
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if not calc or calc.status != 'WAIT':
            return

        _, time = type.split('+')

        if time == '0':
            time = None
        elif time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        calc = calculation.updateCancelAt(
            userId=user.id, id=calc_id, minutes=time)

        if calc:
            if 'stc_' in type:
                await send_confirm_calc_send(bot, call.message, calc_id)
            else:
                await send_calculation(bot, call.message, state, user, calc, is_activate=True)

    if type == 'tr_stop':
        await edit_message(
            bot, call.message, 'text',
            msg_enter_tr_stop(user.lang),
            kb_channel_trailing_stop(user.lang, calc_id)
        )
        await state.set(StatsState.trailing_stop)
        await state.add_data(
            del_mes_id=mes_id,
            calc_id=calc_id
        )

    if 'tr_stop+' in type and 'ch_tr_stop+' not in type:
        _, value = type.split('+')

        if value == '0':
            value = None
        else:
            value = float(value)

        calculation.updateActive(
            userId=user.id, id=calc_id,
            trailingStopCount=value,
            autoTake=None
        )

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc:
            await send_calculation(bot, call.message, state, user, calc, is_activate=True)

    if type == 'auto_stop':
        calc = calculation.get(userId=user.id, calcId=calc_id)

        if calc and calc.ActiveCalc:
            new_val = not calc.ActiveCalc.autoStop
            calculation.updateActive(
                userId=user.id, id=calc_id, autoStop=new_val)
            calc.ActiveCalc.autoStop = new_val

            await send_calculation(bot, call.message, state, user, calc, is_activate=True)

    if type == 'auto_take':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        send_data = channel_calc.getByCalc(calc_id)

        takes = []
        if calc:
            diffOpSl = calc.openPrice - calc.stopLoss
            for el in range(1, 11):
                takes.append(calc.openPrice + diffOpSl * el)

        await edit_message(
            bot, call.message, 'text',
            msg_enter_auto_take(user.lang, takes),
            kb_auto_take(user.lang, calc_id, send_data)
        )

    if 'auto_take+' in type:
        _, val = type.split('+')

        if val == 'null':
            val = None
        else:
            val = float(val)

        calculation.updateActive(
            userId=user.id, id=calc_id, autoTake=val, trailingStopCount=None
        )
        calc = calculation.get(userId=user.id, calcId=calc_id)
        send_data = channel_calc.getByCalc(calc_id)
        if calc:
            await send_calculation(bot, call.message, state, user, calc, is_activate=True)

    if type == 'channel_item':
        await send_admin_channel_calc_item(bot, call.message, state, calc_id, '')

    if type == 'active_end':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if not calc or calc.status != 'DEAL':
            return

        calc = calculation.finishActive(userId=user.id, id=calc_id)

        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'cancel':
        calc = calculation.get(userId=user.id, calcId=calc_id)
        if not calc or calc.status != 'WAIT':
            return

        calc = calculation.update(
            userId=user.id, calcId=calc_id,
            status='CANCEL'
        )

        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'new_stop':
        await bot.edit_message_text(
            msg_enter_new_stop(user.lang),
            chat_id, mes_id,
            reply_markup=kb_calc_back(user.lang, calc_id)
        )
        await state.set(StatsState.new_stop)
        await state.add_data(del_mes_id=mes_id, calc_id=calc_id, type='active_calc')

    if type == 'take_price':
        await state.delete()

        send_data = channel_calc.getByCalc(calc_id)

        await bot.edit_message_text(
            msg_enter_take_price(user.lang), chat_id, mes_id,
            reply_markup=(
                kb_channel_item_back(calc_id) if send_data.sent
                else kb_channel_confirm_back(calc_id)
            ) if send_data else kb_calc_back(user.lang, calc_id)
        )
        await state.set(StatsState.take_price)
        await state.add_data(
            calc_id=calc_id
        )

    if type == 'take_price_yes':
        async with state.data() as data:
            value = data.get('value')

        await state.delete()

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if not calc:
            return

        value_count = (value - calc.openPrice) / \
            (calc.openPrice - calc.stopLoss)

        calculation.updateActive(
            userId=user.id, id=calc_id,
            trailingStopCount=None,
            autoTake=value_count
        )

        calc = calculation.get(userId=user.id, calcId=calc_id)
        if calc:
            await send_calculation(bot, call.message, state, user, calc)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(StatsCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,  # type: ignore
        lambda _: True, pass_bot=True,
        main=stats_factory.filter()
    )
