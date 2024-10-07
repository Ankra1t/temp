from datetime import datetime, timedelta
from math import ceil
import math
import os
from typing import Literal
from telebot.types import InputMediaPhoto
from telebot.async_telebot import AsyncTeleBot

from AuthRoles import first_timeout
from states.stats import ChannelCalcState, StatsState
from common.utils import delete_message, edit_message, edit_message, get_print_float
from data.data import liteDb

from db import db
from Classes import pay_guard, calcService, hti

from messages.common import msg_manuals
from messages.admin import msg_admin_send_settings
from messages.calc import msg_active_options, msg_calc_list, msg_calculation, msg_channel_calc
from messages.errors import msg_sl_op_equal_error
from messages.manual import msg_manual
from messages.profile import msg_user_tariff
from messages.settings import msg_active_settings, msg_atr_settings, msg_change_style_settings, msg_deposit, msg_dop_settings, msg_exchange, msg_maker_or_taker, msg_settings, msg_stop_page, msg_summary_profit_settings
from messages.users import msg_choose_tariff_type, msg_no_tariffs
from messages.common import transl_status
from messages.main import msg_freeze_calc, msg_main, msg_main_freeze, msg_no_uses

from messages.violation import msg_violation
from models import CALC_STATUS_TYPE, MANUAL_TYPE, MARKETS_TYPE, Calculation, Message, StateContext, User
from services import calculation, channel_calc, settings, ticker, violation

from keyboards.channel_post import (
    kb_channel_calc_result, kb_channel_calc_result_stop, kb_channel_calc_result_take,
    kb_channel_post_back, kb_channel_post_list, kb_send_settings, kb_channel_post
)
from keyboards.main import kb_main, kb_violation
from keyboards.manual import kb_manual, kb_manuals
from keyboards.stats import kb_calc_activation, kb_calc_list, kb_confirm_channel_post, kb_freeze_calc, kb_stats_page
from keyboards.tariff import kb_choose_products, kb_tariff_list, kb_user_tariff_back
from keyboards.settings import (
    kb_active_settings, kb_atr_settings, kb_change_deposit, kb_change_style_settings, kb_choose_stop_type, kb_dop_settings, kb_exchange,
    kb_maker_or_taker, kb_settings, kb_summary_profit,
)


async def send_main(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    liteDb.addPagesCount(user.tgId)

    is_valid_use = await pay_guard.valid_use_calc(user.tgId, bot)

    uses_count = db.get_calculator_uses_count(user.id) or 0
    freeze_dt = db.get_user_calc_freeze(user.id)
    unfinished_calc = db.get_unfinished_calc_by_user(user.id)

    if is_valid_use:
        text = msg_main(user.lang, uses_count, True)
    elif freeze_dt is not None:
        text = msg_main_freeze(user.lang, freeze_dt)
    else:
        text = msg_no_uses(user.lang)

    keyboard = kb_main(
        user.lang, user.tgId, is_valid_use, None,
        unfinished_calc is not None
    )

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await edit_message(
            bot, message, 'text', text, keyboard
        )


async def send_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    liteDb.addPagesCount(user.tgId)

    is_risk_update = liteDb.getRiskUpdate(user.tgId)
    u_base = db.get_calc_user_settings(user.id)

    if u_base is None:
        return

    msg = msg_settings(user.lang, u_base, is_risk_update)
    markup = kb_settings(user.lang, user.id)

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        await edit_message(bot, message, 'text', msg, markup)


async def send_dop_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    calc_output = db.get_user_calc_output(user.id)
    is_risk_update = liteDb.getRiskUpdate(user.tgId)

    msg = msg_dop_settings(user.lang, calc_output, is_risk_update)
    markup = kb_dop_settings(user.lang, calc_output, is_risk_update)

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        await edit_message(bot, message, 'text', msg, markup)


async def send_exchange_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    exchange = liteDb.getUserExchange(user.tgId)

    msg = msg_exchange(user.lang, exchange)
    markup = kb_exchange(user.lang, exchange is not None)

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        await edit_message(bot, message, 'text', msg, markup)


async def send_trading_style_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    u_base = db.get_calc_user_settings(user.id)

    style = '-'
    if u_base is not None:
        style = u_base.trading_style or style

    is_style_change = liteDb.getStyleChange(user.tgId)

    msg = msg_change_style_settings(user.lang, style, is_style_change)
    markup = kb_change_style_settings(user.lang, is_style_change)

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        await edit_message(bot, message, 'text', msg, markup)


async def send_active_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    advSettings = settings.getAdvanced(user.id)

    msg = msg_active_settings(user.lang, advSettings)
    kb = kb_active_settings(user.lang, bool(advSettings and advSettings.autoStop))

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=kb
        )
    else:
        await edit_message(bot, message, 'text', msg, kb)


async def send_maker_or_taker(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    info: tuple[str, float, float],
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    msg = msg_maker_or_taker(user.lang, info[1], info[2])
    markup = kb_maker_or_taker(user.lang, *info)

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=markup
        )
    else:
        await edit_message(bot, message, 'text', msg, markup)


async def send_user_deposit(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    stop = liteDb.getUserStop(user.tgId)
    market = db.get_user_current_market(user.id)
    u_base = db.get_calc_user_settings(user.id)

    is_update = False
    if u_base is not None:
        is_update = u_base.is_updating_deposit

    text = msg_deposit(user.lang, u_base, stop)
    keyboard = kb_change_deposit(user.lang, is_update, market)

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_manual_page(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    page: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    text = msg_manuals[page - 1]
    photo = open(f'src/img/info_calc/{page}.jpg', 'rb')
    keyboard = kb_manuals(user.lang, page, len(msg_manuals))

    if is_first:
        await bot.send_photo(
            chat_id, photo, text, 'MarkDown',
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_media(
            InputMediaPhoto(photo, text, 'MarkDown'),  # type: ignore
            chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_summary_profit_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    text = msg_summary_profit_settings(user.lang, user.id)
    kb = kb_summary_profit(user.lang)

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=kb
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


async def send_stats(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    lang = 'en' if user.lang != 'ru' else 'ru'

    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    liteDb.addPagesCount(user.tgId)

    values = calculation.getWeekStats(user.id)

    if values is None:
        return

    texts = {
        'ru': {
            'title': '⚡️ <b>Результаты на эту неделю</b>',

            'title2': '⚡️ Результаты',
            'from': 'с',
            'to': 'по',

            'stop': 'стоп',

            'canceled': 'Отменённые',

            'tp': 'тейков',
            'sl': 'стопов',
            'prices': 'Купил/Продал',
            'result': 'Итого за неделю',
            'long': 'Лонг',
            'short': 'Шорт',
            'success': 'Процент успешных сделок',

            'breakeven': 'безубыток',
        },
        'en': {
            'title': '⚡️ <b>Results for this week</b>',

            'title2': '⚡️ Results',
            'from': 'from',
            'to': 'to',

            'stop': 'stop',

            'canceled': 'Cancelled',

            'tp': 'takes',
            'sl': 'stops',
            'prices': 'Bought/Sold',
            'result': 'Total for the week',
            'long': 'Long',
            'short': 'Short',
            'success': 'Success deals percent',

            'breakeven': 'breakeven',
        },
    }

    msg = f"<b>{texts[lang]['title']}</b>"

    long_count = 0
    short_count = 0

    tool_counts: dict[str, int] = {}

    for valueDate_i, valueDate in enumerate(values):
        date_msg = ''

        tp_count = 0
        sl_count = 0

        success_count = 0
        fail_count = 0

        canceled = ''

        for value_i, value in enumerate(valueDate.get('calcs', [])):
            status: CALC_STATUS_TYPE = value.get('status', 'WAIT')

            valueCount = value.get('valueCount')
            openPrice = value.get('openPrice')
            closePrice = value.get('closePrice')

            tp_sl = ''
            if valueCount is None:
                tp_sl = transl_status(status, lang)
            elif valueCount == 0:
                tp_sl = texts[lang]['breakeven']
            elif valueCount > 0:
                tp_sl = f'{valueCount} {texts[lang]["tp"]}'
                tp_count += valueCount
                success_count += 1
                if closePrice > openPrice:
                    long_count += 1
                else:
                    short_count += 1
            else:
                tp_sl = f'{abs(valueCount)} {texts[lang]["stop"]}'
                sl_count += abs(valueCount)
                fail_count += 1

                if closePrice > openPrice:
                    short_count += 1
                else:
                    long_count += 1

            if value_i == 0:
                date_msg += '\n'

            tool = value.get("tool")
            tool_num = ''
            if tool not in tool_counts:
                tool_counts[tool] = 1
            else:
                tool_counts[tool] += 1
                tool_num = f'_{tool_counts[tool]}'

            if status == 'CANCEL':
                if canceled != '':
                    canceled += ', '
                canceled += f'/<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b>'
            else:
                date = f' ({(datetime.fromisoformat((value.get("createdAt") or "").replace("Z", "")) + timedelta(hours=3)).strftime("%H:%M")})'
                date_msg += f'\n{date} /<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b> - {tp_sl}'

        tp_sl_result = round(tp_count - sl_count, 1)
        tp_sl_show = ''
        if tp_sl_result > 0:
            tp_sl_show = f'{texts[lang]["tp"]}'
        else:
            tp_sl_show = f'{texts[lang]["sl"]}'

        tp_sl_msg = ''
        if tp_count != 0 or sl_count != 0:
            if tp_sl_result == 0:
                tp_sl_msg = f'{texts[lang]["breakeven"]}'
            else:
                tp_sl_msg = f'{"+" if tp_sl_result > 0 else "-"}{abs(tp_sl_result)} {tp_sl_show}'
            tp_sl_msg = f' ({tp_sl_msg})'

        msg += f'\n\n<b><u>{valueDate.get("date")}</u></b>{tp_sl_msg}'
        msg += f'{date_msg}'

        if canceled != '':
            msg += f'\n\n{texts[lang]["canceled"]}: {canceled}'

        if success_count != 0 or fail_count != 0:
            msg += f'\n\n<b>{texts[lang]["success"]}</b>: {round((success_count * 100) / (success_count + fail_count))} %'

    text = msg
    # text = msg_stats_page(user_id, len(calcs))
    kb = kb_stats_page(lang)

    new_mes_id = mes_id
    if is_first:
        new_mes = await bot.send_message(
            chat_id, text,
            reply_markup=kb
        )
        new_mes_id = new_mes.id
    else:
        await edit_message(
            bot, message, 'text', text, kb
        )

    await state.set('user_calc_id live')
    await state.add_data(
        del_mes_id=new_mes_id,
    )


async def send_calc_list(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    list_type: str,
    page=0,
    is_first=False
):
    N = 10

    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    calc_list = None
    if list_type == 'deal':
        calc_list = calculation.getByUserList(user.id, list_type)
    elif list_type == 'canceled':
        calc_list = calculation.getByUserList(user.id, list_type)
    elif list_type == 'wait':
        calc_list = calculation.getByUserList(user.id, list_type)
    elif list_type == 'done':
        calc_list = calculation.getByUserList(user.id, list_type)
    else:
        return

    if calc_list is None:
        return

    calc_list.reverse()

    pages = ceil(len(calc_list) / N)

    calc_list = calc_list[page * N: (page + 1) * N]

    msg = msg_calc_list(user.lang, calc_list, list_type)
    kb = kb_calc_list(user.lang, page, pages, list_type)

    new_mes_id = mes_id
    if is_first:
        new_mes = await bot.send_message(
            chat_id, msg,
            reply_markup=kb
        )
        new_mes_id = new_mes.id
    else:
        await bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=kb
        )

    await state.set(f'user_calc_id {list_type}')
    await state.add_data(
        del_mes_id=new_mes_id,
    )


async def send_user_tariffs(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    text = msg_choose_tariff_type(user.lang)
    keyboard = kb_choose_products(user.lang)

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await edit_message(
            bot, message, 'text', text, keyboard
        )


async def send_tariffs_list_item(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    tariff_type: str,
    page: int,
    is_rus=False,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    tariffs = db.get_prices_by_product(tariff_type, True, True)
    count = len(tariffs)

    if count == 0:
        await bot.edit_message_text(
            msg_no_tariffs(user.lang), chat_id, mes_id,
            reply_markup=kb_user_tariff_back(user.lang)
        )
    else:
        tariff = tariffs[page]
        tariff_id = tariff.id or 0

        if user.lang == 'ru':
            image = tariff.img
        else:
            image = tariff.img_en or tariff.img

        text = msg_user_tariff(tariff)
        keyboard = kb_tariff_list(
            user.lang, tariff_id, count, tariff_type, page, is_rus
        )

        async def send():
            if image is None:
                await bot.send_message(chat_id, text, reply_markup=keyboard)
            else:
                await bot.send_photo(
                    chat_id, image, '',
                    reply_markup=keyboard
                )

        if is_first:
            await send()
        elif message.content_type == 'photo' and image is not None:
            await bot.edit_message_media(
                InputMediaPhoto(image, '', 'HTML'), chat_id, mes_id,
                reply_markup=keyboard
            )
        elif message.content_type == 'text' and image is None:
            await bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )
        else:
            await delete_message(bot, chat_id, mes_id)
            await send()


async def send_calculation(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    calc: Calculation,
    is_first=False,
    is_try=False,
    is_list=False,
    is_activate=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    is_access = await pay_guard.valid_use_calc(user.tgId, bot)

    calc_output = db.get_user_calc_output(user.id)

    if is_list:
        calculation.update(calc.id, openedList=True)

    if is_try:
        kb = None
    if is_activate:
        kb = kb_calc_activation(user.lang, calc)
    else:
        kb = kb_main(
            user.lang, user.tgId,
            is_access, calc,
            is_first=is_try
        )

    if True or calc_output == 'text' or is_try:
        text = msg_calculation(user.lang, calc, is_try)

        if calc.ActiveCalc and (calc.status == 'DEAL' or calc.status == 'WAIT'):
            text = text.strip()
            text += '\n\n' + msg_active_options(user.lang, calc)

        if calc.photo is None:
            if is_first:
                await bot.send_message(chat_id, text, reply_markup=kb)
            else:
                await edit_message(bot, message, 'text', text, kb)
        else:
            if is_first:
                await bot.send_photo(chat_id, calc.photo, text, reply_markup=kb)
            else:
                await edit_message(bot, message, 'photo', text, kb, calc.photo)

    else:
        file_path, caption = hti.create_calculation_image(
            user.tgId, calc
        )

        with open(file_path, 'rb') as photo:
            if not is_first:
                bot.delete_message(chat_id, mes_id)
            await bot.send_photo(
                chat_id, photo, caption=caption,
                reply_markup=kb,
            )
        os.remove(file_path)

    if is_try:
        first_timeout(user.tgId)


async def send_freeze(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    market: MARKETS_TYPE,
    is_first=False
):
    chat_id = message.chat.id

    day_risk = calcService.check_day_risk(user.tgId, market)
    if day_risk:
        await state.set(StatsState.freeze)
        await state.add_data(
            market=market,
        )

        text = msg_freeze_calc(user.lang, day_risk)
        kb = kb_freeze_calc(user.lang)

        if is_first:
            await bot.send_message(
                chat_id, text,
                reply_markup=kb,
            )
        else:
            await edit_message(bot, message, 'text', text, kb)


async def send_confirm_calc_send(
    bot: AsyncTeleBot,
    message: Message,
    stat_id: int,
    is_first=False
):
    chat_id = message.chat.id

    stat = calculation.get(stat_id)
    send_data = channel_calc.getByCalc(stat_id)
    if stat is None or send_data is None:
        return

    info = ticker.get_info(stat.tool or '')

    photo = stat.photo
    text = msg_channel_calc(
        stat, 'ru', send_data.withoutStop, send_data.time or '',
        indexPrice=info and info.indexPrice, percent24h=info and info.price24hPcnt
    )

    text += '\n\nОпрос: ' + ('✅' if send_data.isVote else '❌')
    text += f'\nСк. стоп: {stat.ActiveCalc.trailingStopCount if stat.ActiveCalc and stat.ActiveCalc.trailingStopCount else "-"}'

    kb = kb_confirm_channel_post(
        stat_id
    )

    if is_first:
        if photo is None:
            await bot.send_message(
                chat_id, text,
                reply_markup=kb
            )
        else:
            await bot.send_photo(
                chat_id,
                photo, text,
                reply_markup=kb
            )
    else:
        await edit_message(
            bot,
            message, 'text' if photo is None else 'photo',
            text, kb, photo
        )


async def create_and_send_calc(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    stop_loss: float,
    is_send=True
):
    chat_id = message.chat.id

    async with state.data() as data:
        stat_id = data.get('stat_id')
        calc_type = data.get('calc_type', 'crypto')

        deposit: float = data.get('deposit') or 1.0
        risk: tuple[float, bool] = data.get('risk') or (1., False)
        currency = data.get('currency', 'USD')
        trading_style = data.get('trading_style')
        trading_type = data.get('trading_type') or 'margin'

        open_price: float = data.get('open_price') or 0
        forex = data.get('forex')
        tool = data.get('tool')
        updated_risk = data.get('updated_risk') or 1.
        is_from_deposit = data.get('is_from_deposit') or False

        is_try = data.get('is_try', False)

    if stat_id is not None:
        calc_info = calculation.get(stat_id)
        if calc_info is None or calc_info.ActiveCalc:
            return

        if calc_info.openPrice == stop_loss:
            new_mes = await bot.send_message(chat_id, msg_sl_op_equal_error(user.lang))
            await state.add_data(
                del_mes_id=new_mes.id,
            )
            return

        db.change_calculation_stop_loss(stat_id, stop_loss)
        calc_info.stopLoss = stop_loss

        await send_calculation(bot, message, state, user, calc_info, True)
        await state.delete()
        return

    if open_price == stop_loss:
        new_mes = await bot.send_message(chat_id, msg_sl_op_equal_error(user.lang))
        await state.add_data(
            del_mes_id=new_mes.id,
        )
        return

    u_base = db.get_calc_user_settings(user.id)
    if u_base is None:
        return

    if is_from_deposit:
        count_bet = deposit / open_price
        risk_value = count_bet * abs(open_price - stop_loss)
    else:
        risk_value = risk[0]
        if risk[1]:
            risk_value *= deposit * 0.01

    calc_info = Calculation(
        userId=user.id,
        deposit=deposit,
        riskValue=risk_value * updated_risk,
        openPrice=open_price,
        stopLoss=stop_loss,
        roundCount=u_base.round_count,
        currency=currency,
        market=calc_type,
        tpRatio=u_base.tp_ratio,
        splitValues=u_base.split_values,
        tradingStyle=trading_style or None,
        tool=tool or None,
        forexInfo=forex,
        tradingType=trading_type,
        isFromDeposit=is_from_deposit
    )

    new_id = None
    if not is_try:
        new_id = db.add_calculation(calc_info)
        calc_info.id = new_id

        userExchange = liteDb.getUserExchange(user.tgId)
        if userExchange is not None:
            liteDb.addCalc(new_id, userExchange[0], userExchange[1])

        db.minus_calculator_uses_count(user.id)
        db.delete_unfinished_calc_by_user(user.id)

        db.set_user_base(user.id, 'risk', risk[0])
        db.set_user_risk_is_percent(user.id, risk[1])
        db.set_user_base(user.id, 'deposit', deposit)
        db.set_user_currency(user.id, currency)
    else:
        liteDb.setFirstTry(user.tgId)

    if is_send:
        await send_calculation(bot, message, state, user, calc_info, True, is_try)

    await state.delete()
    return new_id


async def send_stop_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    stop_type = liteDb.getUserStop(user.tgId)
    u_base = db.get_calc_user_settings(user.id)

    current_fd = False
    if u_base is not None:
        current_fd = u_base.is_from_deposit

    atr_settings = liteDb.getUserAtrSettings(user.tgId)

    mes = msg_stop_page(user.lang, atr_settings, stop_type, current_fd)
    kb = kb_choose_stop_type(user.lang)

    if is_first:
        await bot.send_message(
            chat_id, mes,
            reply_markup=kb
        )
    else:
        await bot.edit_message_text(
            mes, chat_id, mes_id,
            reply_markup=kb
        )


async def send_atr_settings(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    atr_settings = liteDb.getUserAtrSettings(user.tgId)

    mes = msg_atr_settings(user.lang, atr_settings)
    kb = kb_atr_settings(user.lang, atr_settings)

    if is_first:
        await bot.send_message(
            chat_id, mes,
            reply_markup=kb
        )
    else:
        await bot.edit_message_text(
            mes, chat_id, mes_id,
            reply_markup=kb
        )


async def send_admin_send_settings(  # TODO - move to admin
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    withoutStop = liteDb.getSendSettings('withoutStop')
    isVote = liteDb.getSendSettings('isVote')
    tradingStyle = liteDb.getSendSettings('style')
    time = liteDb.getSendSettings('time')
    advancedSettings = settings.getAdvanced(user.id)

    msg = msg_admin_send_settings(
        withoutStop == 'False', isVote == 'True', tradingStyle, time,
        advancedSettings and advancedSettings.trailingStop,
        advancedSettings and advancedSettings.cancelMinutes,
    )
    kb = kb_send_settings(withoutStop == 'False', isVote == 'True')

    if is_first:
        await bot.send_message(chat_id, msg, reply_markup=kb)
    else:
        await bot.edit_message_text(
            msg, chat_id, message.id,
            reply_markup=kb
        )


async def send_channel_post(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    msg = '<b><u>Отправка сообщений в канал</u></b>'
    kb = kb_channel_post()

    if is_first:
        await bot.send_message(chat_id, msg, reply_markup=kb)
    else:
        await bot.edit_message_text(
            msg, chat_id, message.id,
            reply_markup=kb
        )


async def send_admin_channel_calc_list(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    page=0,
    is_first=False,
):
    N = 7

    chat_id = message.chat.id
    mes_id = message.id

    inWaitSends = channel_calc.getInWait() or []

    weekStat = channel_calc.getWeekStat()
    stats_link = ''
    if weekStat is not None:
        stats_link = 'Ссылки на статистику:'
        messages = weekStat.get('messages')
        chIds = messages.get('chIds')
        mesIds = messages.get('mesIds')
        langs = messages.get('langs')
        link = ''
        for i in range(1):
            try:
                link = f'https://t.me/c/{chIds[i].replace("-100", "")}/{mesIds[i]}'
            except:
                pass

            stats_link += f'   <a href="{link}">Статистика</a>'

    if len(inWaitSends) == 0:
        mes = '👉 Нет расчётов, требующих действий'
        kb = kb_channel_post_back()

        if is_first:
            await bot.send_message(
                chat_id, mes, reply_markup=kb
            )
        else:
            await bot.edit_message_text(
                mes, chat_id, mes_id,
                reply_markup=kb
            )

        return

    inWaitSends.reverse()
    result_list = inWaitSends[page * N: (page + 1) * N]

    msg = '<b><u>Отправленные расчёты</u></b>'
    if stats_link != '':
        msg += f'\n{stats_link}'
    msg += '\n👇 Нажмите на номер для действий'
    for send_data in result_list:
        calc = calculation.get(send_data.calcId)
        if calc is None:
            continue

        msg += f'\n\n/{send_data.calcId} <b>{(calc.tool or "").replace("/USDT", "")}</b>'
        msg += f' ({datetime.fromisoformat(send_data.createdAt.replace("Z", "")).strftime("%d.%m %H:%M")})'
        msg += f'\nВход/Стоп: <b>{get_print_float(calc.openPrice)} / {get_print_float(calc.newStop or calc.stopLoss)}</b>'

    del_mes_id = mes_id

    kb = kb_channel_post_list(page, math.ceil(len(inWaitSends) / N))
    if is_first:
        new_mes = await bot.send_message(
            chat_id, msg, reply_markup=kb
        )
        del_mes_id = new_mes.id
    else:
        await bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=kb
        )

    await state.set('handle_calc_id')
    await state.add_data(
        del_mes_id=del_mes_id,
    )


async def send_admin_channel_calc_item(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    calc_id: int,
    type: Literal['take', 'stop', ''] = '',
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    send_data = channel_calc.getByCalc(calc_id)
    calc = calculation.get(calc_id)
    if calc is None:
        return

    if send_data is None or (calc.status != 'WAIT' and calc.status != 'DEAL') or calc is None:
        msg = 'Расчёт не найден или не требует действий'
        if is_first:
            await bot.send_message(
                chat_id, msg,
            )
        else:
            await bot.edit_message_text(
                msg, chat_id, mes_id
            )
        return

    link = ''
    if send_data.messages:
        try:
            weekChId = send_data.messages.chIds[0]
            weekMesId = send_data.messages.mesIds[0]
            link = f'https://t.me/c/{weekChId.replace("-100", "")}/{weekMesId}'
        except Exception as e:
            print(e)

    calc_result = calcService.get_result(calc)
    take_info = ''
    for i in range(calc_result.tp_count):
        take_info += f'\n <b>({calc.tpRatio[i]} к 1)</b>: {get_print_float(calc_result.tp_values[i], 5)} USDT'

    cancel_at = '-'
    if calc.cancelAt:
        dt = datetime.fromisoformat(
            calc.cancelAt.replace('Z', '')
        ) + timedelta(hours=3)
        cancel_at = dt.strftime("%d.%m %H:%M")

    msg = f"""<b>{f'<a href="{link}">' if link != '' else ''}{calc.tool}{'</a>' if link != '' else ''}</b>

<b>Объем</b>: {get_print_float(calc_result.count_bet)} монет
<b>Цена входа</b>: {get_print_float(calc.openPrice, 5)} USDT
<b>Стоп-лосс</b>: {get_print_float(calc.newStop or calc.stopLoss, 5)} USDT
<b>Риск</b>: {get_print_float(calc.riskValue, 5)} USDT

<b>Тейки:</b>{take_info}

<b>Время отмены:</b> {cancel_at}
<b>Ск. стоп:</b> {get_print_float(calc.ActiveCalc.trailingStopCount, 1) if calc.ActiveCalc and calc.ActiveCalc.trailingStopCount else '-'}
<b>Вывод стопа:</b> {'❌' if send_data.withoutStop else '✅'}"""

    is_state = True
    if type == 'take':
        kb = kb_channel_calc_result_take(calc.tpRatio, calc_id)
        info = '\n\n<i>Либо введите <b>прибыль</b></i> со сделки'
    elif type == 'stop':
        kb = kb_channel_calc_result_stop(calc_id)
        info = '\n\n<i>Либо введите <b>убыток</b></i> со сделки'
    else:
        kb = kb_channel_calc_result(
            calc.id, calc.status == 'DEAL',
            send_data.withoutStop
        )
        is_state = False
        info = ''

    msg += info

    del_mes_id = mes_id
    if is_first:
        new_mes = await bot.send_message(
            chat_id, msg, reply_markup=kb
        )
        del_mes_id = new_mes.id
    else:
        await bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=kb
        )

    if is_state:
        await state.set(ChannelCalcState.loss)
        await state.add_data(
            del_mes_id=del_mes_id,
            stat_id=calc_id,
            type=type
        )


async def send_manual(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    type: MANUAL_TYPE = 'calc',
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()

    msg = msg_manual(user.lang, type)
    kb = kb_manual(user.lang)

    text = db.get_text_by_name(type)
    photo = None
    if text is not None:
        if user.lang == 'ru':
            photo = text.media_id
        else:
            photo = text.media_id_en

    if is_first:
        if photo is None:
            await bot.send_photo(
                chat_id, photo, msg,
                reply_markup=kb
            )
        else:
            await bot.send_message(
                chat_id, msg,
                reply_markup=kb
            )
    else:
        if photo is None:
            message_type = 'text'
        else:
            message_type = 'photo'

        try:
            await edit_message(
                bot, message, message_type,
                msg, kb, photo
            )
        except:
            pass


async def send_violation(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_edit=False,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    current = violation.getMonthPoints(user.id)
    if current is None:
        return

    isToday = violation.getToday(user.id) is not None

    msg = msg_violation(
        user.lang,
        current.get('points'),
        isToday,
        current.get('result'),
        is_edit
    )

    kb = kb_violation(user.lang, isToday, current.get(
        'canEdit', False), is_edit)

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=kb
        )
    else:
        await bot.edit_message_text(
            msg,
            chat_id, mes_id,
            reply_markup=kb
        )
