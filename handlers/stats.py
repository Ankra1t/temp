import re
from datetime import timedelta, datetime
from telebot.async_telebot import AsyncTeleBot

# TODO - each state import from states
from states.settings import ViolationState
from states.stats import ChannelCalcState

from config_logger import logger
from Classes import calcService
from CHANNEL.channel_post import channel_post
from models import Message, StateContext, User
from db import db
from common.utils import delete_message, digit_accept, text_accept
from common.dt import get_datetime_now, get_str_by_datetime

from pages.calculate import send_admin_channel_calc_item, send_admin_channel_calc_list, send_admin_send_settings, send_stats, send_violation, send_calculation, send_freeze, send_confirm_calc_send
from keyboards.main import kb_violation_skip
from keyboards.stats import kb_deal_profit_minus, kb_calc_image_text

from states.stats import StatsState
from messages.errros import msg_digit_error, msg_freeze_error, msg_text_error
from messages.main import msg_frozen
from services import calculation, channel_calc, settings, ticker, violation


async def handle_loss(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        stat_id = data.get('stat_id', 0)

    value = digit_accept(message)
    if value is None:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_deal_profit_minus(user.lang, stat_id)
        )
        return

    logger.info(f'callback "handle_loss" user_tg_id={user.tgId} value={value}')

    calcService.set_profit(stat_id, -abs(value))
    calc_info = calculation.get(stat_id)
    if calc_info is None:
        return

    calculation.update(
        stat_id, status='FINISH'
    )

    send_data = channel_calc.getByCalc(stat_id)
    if send_data is not None:
        tickerInfo = ticker.get_info(calc_info.tool or '')
        await channel_post.send_calc(calc_info, send_data, tickerInfo and tickerInfo.indexPrice)

    await send_calculation(bot, message, state, user, calc_info, True)
    await send_freeze(bot, message, state, user, calc_info.market, True)


async def handle_sum(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        stat_id = data.get('stat_id', 0)

    value = digit_accept(message)
    if value is None or value < 0:
        await bot.send_message(
            chat_id, msg_digit_error(user.lang, 0),
            reply_markup=kb_deal_profit_minus(user.lang, stat_id)
        )
        return

    logger.info(f'callback "handle_sum" user_tg_id={user.tgId} value={value}')

    calcService.set_profit(stat_id, value)
    calc_info = calculation.get(stat_id)
    if calc_info is None:
        return

    calculation.update(
        stat_id, status='FINISH'
    )

    send_data = channel_calc.getByCalc(stat_id)
    if send_data is not None:
        tickerInfo = ticker.get_info(calc_info.tool or '')
        await channel_post.send_calc(calc_info, send_data, tickerInfo and tickerInfo.indexPrice)

    await send_calculation(bot, message, state, user, calc_info, True)
    await send_freeze(bot, message, state, user, calc_info.market, True)


async def handle_freeze_dt(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        market = data.get('market')

    value = text_accept(message) or ''

    logger.info(
        f'callback "handle_freeze_dt" user_tg_id={user.tgId} value={value}')

    try:
        time_reg = r'^([0-1]?[0-9]|2[0-3]):[0-5]?[0-9]$'

        if re.match(time_reg, value) is not None:
            hours, minutes = value.split(':')
            finish_freeze = get_datetime_now() + timedelta(hours=int(hours), minutes=int(minutes))
        else:
            date, time = value.split(' ')
            day, month, year = date.split('.')
            hours, minutes = time.split(':')

            if len(year) == 2:
                year = '20' + year

            finish_freeze = datetime(
                int(year), int(month), int(day),
                int(hours), int(minutes)
            ) - timedelta(hours=3)
    except:
        await bot.send_message(
            chat_id, msg_freeze_error(user.lang),
        )
        return

    db.set_user_calc_freeze(user.id, finish_freeze, market)
    await bot.send_message(
        chat_id,
        msg_frozen(user.lang, get_str_by_datetime(finish_freeze))
    )
    await state.delete()


async def handle_calc_image_text(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_text = data.get('calc_text', 'J')
        stat_id = data.get('stat_id', 0)
        type = data.get('type', '')

    await delete_message(bot, chat_id, message.id)

    if message.content_type != 'photo' and message.content_type != 'text':
        new_mes = await bot.send_message(
            chat_id, calc_text,
            reply_markup=kb_calc_image_text(user.lang, stat_id)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    text = message.html_caption or message.html_text
    photo = None
    if message.photo is not None:
        photo = message.photo[0].file_id

    data = {}

    calc = calculation.get(stat_id)
    if calc is None:
        return

    if photo:
        data['photo'] = photo

    if text:
        if calc.status == 'FINISH' or type == 'stats':
            now = get_datetime_now() + timedelta(hours=3)
            data['comment'] = (
                (calc.comment or '') +
                f'\n{now.strftime("%H:%M")} - '
                + text
            ).strip()
        else:
            data['description'] = text

    calc = calculation.update(
        stat_id,
        **data
    )
    if calc is None:
        return

    await state.delete()

    if type != 'stats':
        await send_calculation(bot, message, state, user, calc, True)
    else:
        send_data = channel_calc.getByCalc(calc.id)
        if send_data:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice)

        await send_admin_channel_calc_item(
            bot, message, state, stat_id, is_first=True
        )


async def handle_send_text(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    new_text = message.html_text
    if new_text is None:
        new_mes = await bot.send_message(
            chat_id, 'Введите текст:'
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    async with state.data() as data:
        stat_id = data['stat_id']

    calculation.update(stat_id, description=new_text)

    await state.delete()
    await send_confirm_calc_send(bot, message, stat_id, True)


async def handle_send_photo(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    new_photo = message.photo[0] \
        if message.photo is not None and len(message.photo) > 0 \
        else None

    if new_photo is None:
        new_mes = await bot.send_message(
            chat_id, 'Отправьте фото:'
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    async with state.data() as data:
        stat_id = data.get('stat_id', 0)

    calculation.update(stat_id, photo=new_photo.file_id)

    await state.delete()
    await send_confirm_calc_send(bot, message, stat_id, True)


async def handle_channel_calc_loss(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        stat_id = data.get('stat_id', 0)
        is_calc = data.get('is_calc')
        type = data.get('type')

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    calcService.set_profit(stat_id, abs(value) * (-1 if type == 'stop' else 1))
    calc = calculation.get(stat_id)
    if calc is None:
        return

    calculation.update(
        stat_id, status='FINISH'
    )

    await state.delete()
    send_data = channel_calc.getByCalc(stat_id)
    if send_data is not None:
        tickerInfo = ticker.get_info(calc.tool or '')
        await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice)

        if is_calc:
            await send_calculation(bot, message, state, user, calc, True)
        else:
            await send_admin_channel_calc_list(bot, message, state, is_first=True)
    else:
        if is_calc:
            await send_calculation(bot, message, state, user, calc, True)
        else:
            await send_stats(bot, message, state, user, True)


async def handle_violation_message(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        violation_id = data.get('violation_id', 0)

    if message.content_type != 'photo' and message.content_type != 'text':
        new_mes = await bot.send_message(
            chat_id, msg_text_error(user.lang),
            reply_markup=kb_violation_skip(user.lang)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    text = message.html_caption or message.html_text
    photo = None
    if message.photo is not None:
        photo = message.photo[0].file_id

    violation.update(
        violation_id,
        text,
        photo
    )

    await state.delete()
    await send_violation(bot, message, state, user, is_first=True)


async def handle_cancel_at(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_id = data.get('calc_id', 0)
        action = data.get('action', '')

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    value = round(value, 2)

    if action == 'send_settings':
        settings.updateAdvanced(user.id, cancelMinutes=value)
        await send_admin_send_settings(bot, message, state, user, True)
    else:
        calc = calculation.updateCancelAt(calc_id, int(value * 60))

        if calc:
            send_data = channel_calc.getByCalc(calc.id)
            if action == 'send_data' and send_data is not None:
                await send_admin_channel_calc_item(
                    bot, message, state, calc.id, is_first=True
                )
            else:
                await send_calculation(bot, message, state, user, calc, True)


async def handle_new_stop(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_id = data.get('calc_id', 0)

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    calc = calculation.update(calc_id, newStop=value)

    if calc:
        await send_admin_channel_calc_item(
            bot, message, state, calc.id, is_first=True
        )


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_sum, state=StatsState.sum)
    reg_mes(handle_loss, state=StatsState.loss)
    reg_mes(handle_freeze_dt, state=StatsState.freeze)
    reg_mes(handle_calc_image_text, state=StatsState.add_image_text,
            content_types=['message', 'photo'])

    reg_mes(handle_send_text, state=StatsState.send_add_text)
    reg_mes(handle_send_photo, state=StatsState.send_add_photo,
            content_types=['message', 'photo'])

    reg_mes(handle_cancel_at, state=StatsState.cancel_at)
    reg_mes(handle_new_stop, state=StatsState.new_stop)

    reg_mes(handle_channel_calc_loss, state=ChannelCalcState.loss)
    reg_mes(handle_violation_message, state=ViolationState.message)
