import re
from datetime import timedelta, datetime
from telebot.async_telebot import AsyncTeleBot

# TODO - импортировать все состояния из states
from common.calculation import getStrValueCount
from common.vars import DATETIME_PATTERN
from states.settings import ViolationState
from states.stats import ChannelCalcState

from config_logger import logger
from models import Message, StateContext, User
from common.utils import delete_message, digit_accept, get_print_float, is_digit
from common.dt import get_datetime_by_str, get_datetime_now

from pages.calculate import send_active_settings, send_admin_channel_calc_item, send_admin_channel_calc_list, send_admin_send_settings, send_stats, send_violation, send_calculation, send_confirm_calc_send
from keyboards.main import kb_violation_skip
from keyboards.stats import kb_confirm_take_price, kb_deal_profit_cancel, kb_deal_profit_minus, kb_calc_image_text

from states.stats import StatsState
from messages.errors import msg_digit_error, msg_text_error
from service.advanced_settings_storage import advanced_settings_storage


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

    # TODO - удаляем, теперь нельзя выставлять профит
    # calcService.set_profit(
    #     user.tgId,
    #     stat_id, -abs(value))
    # TODO - calculation.get(userId=user.id, calcId=stat_id)
    calc_info = None
    if calc_info is None:
        return

    # TODO - calculation.update(userId=user.id, calcId=stat_id, status='FINISH')

    await send_calculation(bot, message, state, user, calc_info, True)


async def handle_close_price(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_id = data.get('calc_id', 0)

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_deal_profit_cancel(user.lang, calc_id)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_close_price" user_tg_id={user.tgId} value={value}')

    # TODO - calculation.get(userId=user.id, calcId=calc_id)
    calc = None
    # TODO - Получение инфо о данных по каналу
    send_data = None
    if calc is None or (calc and calc.ActiveCalc and not send_data):
        return

    if calc is None:
        return

    value_count = (value - calc.openPrice) / (calc.openPrice - calc.stopLoss)

    # TODO - удаляем, теперь нельзя выставлять профит
    # calcService.set_profit(
    #     user.tgId,
    #     calc_id, calc.riskValue * value_count)
    # TODO - calculation.update(userId=user.id, calcId=calc_id, status='FINISH')

    if calc:
        await send_calculation(bot, message, state, user, calc, True)


async def handle_take_price(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_id = data.get('calc_id', 0)

    value = digit_accept(message)
    if value is None:
        # TODO - channel_calc.getByCalc(calc_id)
        send_data = None

        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
            reply_markup=kb_deal_profit_cancel(user.lang, calc_id)
            # reply_markup=(
            #     kb_channel_item_back(calc_id) if send_data.sent
            #     else kb_channel_confirm_back(calc_id)
            # ) if send_data else kb_deal_profit_cancel(user.lang, calc_id)
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    logger.info(
        f'callback "handle_take_price" user_tg_id={user.tgId} value={value}')

    # TODO - calculation.get(userId=user.id, calcId=calc_id)
    calc = None
    if calc is None or (calc.ActiveCalc is None):
        return

    value_count = (value - calc.openPrice) / (calc.openPrice - calc.stopLoss)

    await state.add_data(
        value=value
    )

    msg = ''
    if user.lang == 'ru':
        if calc.ActiveCalc.autoTake:
            msg = f'Текущий тейк <b>{get_print_float(calc.ActiveCalc.autoTake, 1)}</b> тейков перезапишется'
        elif calc.ActiveCalc.trailingStopCount:
            msg = f'Текущий скользящий стоп каждый {get_print_float(calc.ActiveCalc.trailingStopCount, 1)} тейка перезапишется'
        msg += f'\nВыставляем {getStrValueCount(value_count)} ({value} USDT)?'
    else:
        if calc.ActiveCalc.autoTake:
            msg = f'Current take <b>{get_print_float(calc.ActiveCalc.autoTake, 1)}</b> takes will overwritten'
        elif calc.ActiveCalc.trailingStopCount:
            msg = f'Current trailing stop {get_print_float(calc.ActiveCalc.trailingStopCount, 1)} takes will overwritten'
        msg += f'\nSet {getStrValueCount(value_count)} ({value} USDT)?'

    await bot.send_message(
        chat_id, msg,
        reply_markup=kb_confirm_take_price(user.lang, calc_id)
    )


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

    # TODO - удаляем, теперь нельзя выставлять профит
    # calcService.set_profit(
    #     user.tgId,
    #     stat_id, value)
    # TODO - calculation.get(userId=user.id, calcId=stat_id)
    calc_info = None
    if calc_info is None:
        return

    # TODO - calculation.update(userId=user.id, calcId=stat_id, status='FINISH')

    await send_calculation(bot, message, state, user, calc_info, True)


async def handle_calc_image_text(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_text = data.get('calc_text', 'J')
        stat_id = data.get('stat_id', 0)
        type = data.get('type', '')
        action = data.get('action', '')

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
        photo = message.photo[-1].file_id

    data = {}

    # TODO - calculation.get(userId=user.id, calcId=stat_id)
    calc = None
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

    # TODO - calculation.update(userId=user.id, calcId=stat_id, **data)
    if calc is None:
        return

    await state.delete()

    if type == 'stc':
        await send_confirm_calc_send(bot, message, calc.id, True)
    elif type != 'stats':
        await send_calculation(bot, message, state, user, calc, True)
    else:
        await send_admin_channel_calc_item(
            bot, message, state, stat_id, is_first=True
        )


async def handle_send_text(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
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

    # TODO - calculation.update(userId=user.id, calcId=stat_id, description=new_text)

    await state.delete()
    await send_confirm_calc_send(bot, message, stat_id, True)


async def handle_send_photo(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
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

    # TODO - calculation.update(userId=user.id, calcId=stat_id, photo=new_photo.file_id)

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

    # TODO - calculation.get(userId=user.id, calcId=stat_id)
    calc = None
    # TODO - channel_calc.getByCalc(stat_id)
    send_data = None

    if calc and not (calc.ActiveCalc and not send_data):
        # TODO - удаляем, теперь нельзя выставлять профит
        # calcService.set_profit(
        #     user.tgId,
        #     stat_id,
        #     abs(value) * (-1 if type == 'stop' else 1)
        # )
        # TODO - calculation.update(userId=user.id, calcId=stat_id, status='FINISH')
        pass

    if not calc:
        return

    if is_calc:
        await send_calculation(bot, message, state, user, calc, True)
    else:
        if send_data is not None:
            await send_admin_channel_calc_list(bot, message, state, is_first=True)
        else:
            await send_stats(bot, message, state, user, True)

    await state.delete()


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

    # TODO - Обновить инфо о нарушениях
    # violation.update(
    #     violation_id,
    #     text,
    #     photo
    # )

    await state.delete()
    await send_violation(bot, message, state, user, is_first=True)


async def handle_cancel_at(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_id = data.get('calc_id', 0)
        action = data.get('action', '')

    is_settings = 'settings' in action

    value = message.text
    if (
        (value is None) or
        (is_settings and not is_digit(value)) or
        (
            not is_settings and not (
                re.search(DATETIME_PATTERN, value) is not None or
                is_digit(value)
            )
        )
    ):
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    if is_digit(value):
        value = int(float(value) * 60)
    else:
        dt = get_datetime_by_str(value) or datetime.now()

        value = int(
            abs((int(datetime.now().timestamp()) - int(dt.timestamp())) / 60)
        )

    if is_settings:
        advanced_settings_storage.update_advanced(user.id, cancelMinutes=value)

    if action == 'settings':
        await send_active_settings(bot, message, state, user, True)
    elif action == 'send_settings':
        await send_admin_send_settings(bot, message, state, user, True)
    else:
        # TODO - calculation.updateCancelAt(userId=user.id, id=calc_id, minutes=value)
        calc = None

        if calc:
            # TODO - channel_calc.getByCalc(calc.id)
            send_data = None

            if 'stc' in action:
                await send_confirm_calc_send(bot, message, calc_id, True)
            # elif action == 'send_data' and send_data is not None:
            #     await send_admin_channel_calc_item(
            #         bot, message, state, calc.id, is_first=True
            #     )
            else:
                await send_calculation(bot, message, state, user, calc, True, is_activate=True)

    await state.delete()


async def handle_new_stop(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        calc_id = data.get('calc_id', 0)
        type = data.get('type', '')

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error(user.lang),
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    # TODO - calculation.get(userId=user.id, calcId=calc_id)
    calc = None
    if calc is None:
        return

    # TODO - Получения информации по монете
    ticker_info = None

    diffOpSl = calc.openPrice - calc.stopLoss

    if not (ticker_info and ticker_info.indexPrice) or (
        (diffOpSl > 0 and value > ticker_info.indexPrice) or
        (diffOpSl < 0 and value < ticker_info.indexPrice)
    ):
        new_mes = await bot.send_message(
            chat_id, 'Цена стопа не может быть выше текущей цены инструмента\nВведите другое значение:',
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    # TODO - calculation.update(userId=user.id, calcId=calc_id, newStop=value)

    if calc:
        if type == 'active_calc':
            await send_calculation(bot, message, state, user, calc, True)
        else:
            await send_admin_channel_calc_item(
                bot, message, state, calc.id, is_first=True
            )

    await state.delete()


async def handle_trailing_stop(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
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

    if action == 'settings':
        advanced_settings_storage.update_advanced(
            user.id, trailingStop=value, autoTake=None)
        await send_active_settings(bot, message, state, user, True)
    else:
        # TODO - calculation.updateActive(userId=user.id, id=calc_id, trailingStopCount=value, autoTake=None)

        # TODO - calculation.get(userId=user.id, calcId=calc_id)
        calc = None
        if calc:
            await send_calculation(bot, message, state, user, calc, True, is_activate=True)

    await state.delete()


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_sum, state=StatsState.sum)
    reg_mes(handle_loss, state=StatsState.loss)
    reg_mes(handle_close_price, state=StatsState.close_price)
    reg_mes(handle_take_price, state=StatsState.take_price)
    reg_mes(
        handle_calc_image_text, state=StatsState.add_image_text,
        content_types=['text', 'photo']
    )

    reg_mes(handle_send_text, state=StatsState.send_add_text)
    reg_mes(
        handle_send_photo, state=StatsState.send_add_photo,
        content_types=['text', 'photo']
    )

    reg_mes(handle_cancel_at, state=StatsState.cancel_at)
    reg_mes(handle_new_stop, state=StatsState.new_stop)
    reg_mes(handle_trailing_stop, state=StatsState.trailing_stop)

    reg_mes(handle_channel_calc_loss, state=ChannelCalcState.loss)
    reg_mes(handle_violation_message, state=ViolationState.message)
