from datetime import timedelta
import os
from random import randint
from time import sleep
from typing import Literal
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from AuthRoles import vote_timeout
from CHANNEL.channel_post import channel_post

from states.calculate import CalculateState, ForexCalcState
from states.stats import ChannelCalcState, StatsState

from common.calculation import get_count_value_bet
from common.utils import delete_message, edit_message
from common.dt import get_datetime_now, get_str_by_datetime

from data.data import liteDb
from config_global import EN_CHANNEL_ID, PROD, RU_CHANNEL_ID
from config_logger import logger

from db import db
from Classes import calcService, pay_guard
from messages.stats import msg_market_stats
from models import MARKETS_TYPE, CallbackQuery, StateContext, User
from services import calculation, channel_calc, ticker

# TODO - months в commmon файл
from messages.calc import msg_calculate_change, msg_calculate_delete, msg_calculation, msg_calculation_deleted, msg_channel_calculation
from messages.enter import msg_enter_calc_img_text, msg_enter_cancel_at, msg_enter_open_price, msg_enter_pair, msg_enter_profit_minus, msg_enter_profit_sum, msg_enter_save_calc, msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style
from messages.main import msg_frozen

from keyboards.settings import kb_take_profit, kb_trading_style
from keyboards.channel_post import kb_channel_calc_result_stop, kb_channel_calc_result_take
from keyboards.main import kb_main
from keyboards.stats import (
    kb_cancel_at, stats_factory, StatsCallbackFilter,
    kb_calc_image_text, kb_calc_result, kb_calculate_change,
    kb_calculate_delete, kb_confirm_channel_post, kb_deal_profit_cancel,
    kb_deal_profit_minus, kb_deal_result, kb_send_back, kb_send_calc_time, kb_stats,
)
from pages.calculate import send_calc_list, send_calculation, send_confirm_calc_send, send_freeze, send_main, send_stats


channels = (RU_CHANNEL_ID, EN_CHANNEL_ID)


def createScreen(
    tool: str,
    time: Literal['1h', '4h', '1d'] = '1h',
    type: Literal['bars', 'candles'] = 'bars',
    scale=0
):
    print('START')
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if PROD:
        options.add_argument('--headless')
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("start-maximized")

    browser = wd.Chrome(
        options=options,
        service=Service(
            executable_path='/usr/bin/chromedriver' if PROD else None,  # type:ignore
        )
        # service=Service(ChromeDriverManager().install())
    )
    browser.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    browser.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
    }
    )
    # browser.maximize_window()

    browser.get(
        f'https://www.bybit.com/trade/usdt/{tool.replace("/", "").upper()}'
    )

    print(browser.title)

    print(browser.page_source)

    performance_log = browser.get_log('performance')
    print(str(performance_log).strip('[]'))

    for entry in browser.get_log('performance'):
        print(entry)

    if not PROD:
        browser.execute_script(
            "localStorage.setItem(arguments[0], arguments[1])", 'BYBIT_THEME_KEY', 'light'
        )
        browser.refresh()

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, 'self-tool--time-interval-item')
        )
    )
    print('GET ELEMENT')
    interval_buttons = browser.find_elements(
        By.CLASS_NAME, 'self-tool--time-interval-item'
    )
    print('GET ELEMENTS')
    print(interval_buttons)
    for el in interval_buttons:
        if el.text == time:
            el.click()

    fulscreen_btn = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, 'iconicon_fullscreen_on')
        )
    )
    fulscreen_btn.click()

    bars_select = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.self-tool__padding-horizen.flex-align-center.tv-self--chart-type-anchor.pointer.hover-color-white')
        )
    )
    ActionChains(browser).move_to_element(bars_select).perform()

    bars_btn = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, f'iconicon_ktv_{type}')
        )
    )
    bars_btn.click()

    click_place = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, 'self-tv_tool-header')
        )
    )
    ActionChains(browser).move_to_element_with_offset(
        click_place, randint(100, 600), 30
    ).context_click().move_by_offset(
        50, 250
    ).click().perform()

    scale = min(max(scale, 0), 10)
    mas = [Keys.UP for _ in range(scale)]
    ActionChains(browser).key_down(Keys.CONTROL).send_keys(*mas).perform()

    go_away = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, 'by-footer-derivatives__bg')
        )
    )
    ActionChains(browser).move_to_element(
        go_away
    ).perform()

    sleep(2)
    table = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(
            (By.ID, "tv_chart_container")
        )
    )

    file_path = '_calc_images/table.png'
    table.screenshot(file_path)
    browser.close()

    return file_path


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

    if 'time+' in type:
        _, time = type.split('+')
        date = get_datetime_now() + timedelta(hours=int(time))

        async with state.data() as data:
            market: MARKETS_TYPE | None = data.get('market')

        db.set_user_calc_freeze(user.id, date, market)

        await bot.edit_message_text(
            msg_frozen(user.lang, get_str_by_datetime(date)),
            chat_id, mes_id
        )
        await state.delete()

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

            calc_info = calculation.get(calc_id)
            if calc_info is None:
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
                    rate = float(profit.replace('loss', ''))
                    _, _, spot_rate = get_count_value_bet(calc_info)
                    calcService.set_profit(
                        calc_id, -calc_info.riskValue * rate * spot_rate
                    )
                elif profit != 'cancel':
                    _, _, spot_rate = get_count_value_bet(calc_info)
                    profit_result = calc_info.riskValue * \
                        int(profit) * spot_rate
                    calcService.set_profit(calc_id, profit_result)
                else:
                    is_cancel = True

                calc_info = calculation.get(calc_id)
                if calc_info is None:
                    return

                await send_calculation(bot, call.message, state, user, calc_info)

                if not is_cancel:
                    calculation.update(
                        calc_id, status='FINISH'
                    )
                    send_data = channel_calc.getByCalc(calc_id)
                    if send_data is not None:
                        tickerInfo = ticker.get_info(calc_info.tool or '')
                        await channel_post.send_calc(calc_info, send_data, tickerInfo and tickerInfo.indexPrice)
                    await send_freeze(
                        bot, call.message, state, user,
                        calc_info.market, True
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
        calc = calculation.get(calc_id)
        if calc is not None and not calc.openedList:
            try:
                await bot.edit_message_reply_markup(
                    chat_id, mes_id,
                    reply_markup=kb_calc_result(user.lang, user.id, calc)
                )
            except:
                pass

        await send_stats(
            bot, call.message, state, user,
            calc is not None and not calc.openedList
        )

    if type == 'stats_market':
        stats = calcService.get_stats(user.tgId, stats_market)
        text = msg_market_stats(user.lang, stats_market, stats)

        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_stats(user.lang, 'market')
        )

    if type == 'back_calc':
        calc = calculation.get(calc_id)
        if calc is not None:
            await send_calculation(bot, call.message, state, user, calc)

    if type == 'result_calc':
        calc = calculation.get(calc_id)
        if calc is not None:
            is_access = await pay_guard.valid_use_calc(user.tgId, bot)
            await bot.edit_message_reply_markup(
                chat_id, mes_id,
                reply_markup=kb_calc_result(user.lang, user.id, calc, True)
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

            is_valid = await pay_guard.valid_use_calc(user.tgId, bot)
            calc_info = calculation.get(calc_id)

            await edit_message(
                bot, call.message, prev_type,  # type: ignore
                text,
                kb_main(user.lang, user.tgId, is_valid, calc_info),
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

            await edit_message(
                bot, call.message, prev_type,  # type: ignore
                msg_calculate_change(user.lang, text),
                kb_calculate_change(user.lang, calc_id),
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

            is_valid = await pay_guard.valid_use_calc(user.tgId, bot)
            calc_info = calculation.get(calc_id)

            await edit_message(
                bot, call.message, prev_type,  # type: ignore
                text,
                kb_main(user.lang, user.tgId, is_valid, calc_info),
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
            calc = calculation.get(calc_id)
            if calc is None:
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
            calc = calculation.get(calc_id)

            if calc:
                await bot.edit_message_text(
                    msg_calculation(user.lang, calc),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(
                        user.lang, calc.tpRatio, calc.id)
                )

    if 'tp_rate+' in type:
        _, rate = type.split('+')
        rate = int(rate)

        calc = calculation.get(calc_id)
        if calc and len(calc.tpRatio) != 1:
            if rate in calc.tpRatio:
                calc.tpRatio.remove(rate)
            else:
                calc.tpRatio.append(rate)
                calc.tpRatio.sort()

            calc = calculation.update(calc.id, tpRatio=calc.tpRatio)
            if calc:
                await bot.edit_message_text(
                    msg_calculation(user.lang, calc),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(
                        user.lang, calc.tpRatio, calc.id)
                )

    if type == 'remove_img_text':
        calc = calculation.update(calc_id, photo=None, description=None)
        if calc is None:
            return
        await send_calculation(bot, call.message, state, user, calc)

    if type == 'add_img_text':
        calc = calculation.get(calc_id)
        if calc is None:
            return

        text = msg_enter_calc_img_text(user.lang, calc)
        kb = kb_calc_image_text(user.lang, calc)

        new_mes_id = await edit_message(bot, call.message, 'text', text, kb)

        await state.set(StatsState.add_image_text)
        await state.add_data(
            stat_id=calc_id,
            calc_text=text,
            del_mes_id=new_mes_id,
        )

    if type == 'comment':
        calc = calculation.get(calc_id)
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
        calc = calculation.get(calc_id)
        if calc is None:
            return

        withoutStop = liteDb.getSendSettings('withoutStop')
        style = liteDb.getSendSettings('style')
        isVote = liteDb.getSendSettings('isVote')
        time = liteDb.getSendSettings('time')

        send_data = channel_calc.create(calc_id)
        if send_data is None:
            return

        if withoutStop == 'True' or calc.stopLoss == -1:
            channel_calc.update(send_data.id, withoutStop=True)
        if isVote == 'False':
            channel_calc.update(send_data.id, isVote=False)
        if style:
            db.change_calculation_style(calc_id, style)
            channel_calc.update(send_data.id, tradingStyle=style)
        if time:
            channel_calc.update(send_data.id, time=time)

        await bot.edit_message_reply_markup(
            chat_id, mes_id,
            reply_markup=kb_calc_result(
                user.lang, user.id, calc
            )
        )
        await send_confirm_calc_send(bot, call.message, calc_id, True)

    if type == 'stc+send':
        send_data = channel_calc.getByCalc(calc_id)
        calc = calculation.get(calc_id)
        if send_data is None or calc is None:
            return

        photo = calc.photo

        sent_today = len(channel_calc.getSentToday() or [])

        mesIds: list[int] = []
        for i, CHANNEL_ID in enumerate(channels):
            ch_lang = 'ru' if i == 0 else 'en'

            tickerInfo = ticker.get_info(calc.tool or '')

            weekStat = channel_calc.getWeekStat()
            link = ''
            if weekStat:
                messages = weekStat.get('messages')
                try:
                    weekMesId = messages.get('mesIds', [])[0]
                    weekСhId = messages.get('chIds', [])[0]
                    link = f'https://t.me/c/{weekСhId.replace("-100", "")}/{weekMesId}'
                except:
                    pass

            text = msg_channel_calculation(
                calc, ch_lang, send_data.withoutStop, send_data.time or '', sent_today + 1,
                indexPrice=tickerInfo and tickerInfo.indexPrice,
                description=calc.description if ch_lang == 'ru' else None,
                week_stat_link=link,
                try_link=f'https://t.me/{(await bot.get_me()).username}?start=calc_{calc_id}'
            )

            if photo is None:
                new_mes = await bot.send_message(
                    CHANNEL_ID, text,
                    disable_web_page_preview=True
                )
            else:
                new_mes = await bot.send_photo(
                    CHANNEL_ID,
                    photo, text,
                )

            mesIds.append(new_mes.id)

        await bot.delete_message(chat_id, mes_id)
        await bot.send_message(chat_id, '✅ Отправлено')

        channel_calc.update(
            send_data.id,
            sent=True,
            messages={
                'chIds': [str(el) for el in channels],
                'mesIds': [str(el) for el in mesIds],
                'langs': ['ru', 'en'],
            }
        )

        await channel_post.send_stats()

        live = channel_calc.getLiveInfo()
        if live:
            await channel_post.send_live(live, calc)

        if send_data.isVote:
            seconds = vote_timeout(calc_id)
            new_mes = await bot.send_message(
                chat_id, f'Опрос будет отправлен через {round(seconds, 1)} секунд'
            )
            channel_post.loading_vote_message_ids[calc_id] = (chat_id, new_mes.id) # TODO - создать метод класса

        await send_main(bot, call.message, state, user, True)

    if type == 'stc+rescreen':
        send_data = channel_calc.getByCalc(calc_id)
        calc = calculation.get(calc_id)
        if calc is None or send_data is None:
            return

        new_mes = await bot.send_message(
            chat_id, 'Генерация изображения...',
        )

        try:
            file_path = createScreen(
                (calc.tool or '').replace('/', '').upper(),
                '1h', 'candles', 6
            )
        except Exception as e:
            print(e)
            file_path = None

        text = msg_channel_calculation(
            calc, 'ru', send_data.withoutStop, send_data.time or '',
            description=calc.description
        )

        if file_path is None:
            await bot.edit_message_text(
                'Ошибка генерации фото', new_mes.chat.id, new_mes.id,
            )

            main_mes = await bot.send_message(
                chat_id, text,
                reply_markup=kb_confirm_channel_post(
                    calc_id
                )
            )
        else:
            await bot.delete_message(new_mes.chat.id, new_mes.id)

            with open(file_path, 'rb') as photo:
                main_mes = await bot.send_photo(
                    chat_id, photo, text,
                    reply_markup=kb_confirm_channel_post(
                        calc_id
                    )
                )
            os.remove(file_path)

        photo_str = None
        if main_mes.photo is not None and len(main_mes.photo) > 0:
            photo_str = main_mes.photo[-1].file_id

        calculation.update(calc_id, photo=photo_str)
        await bot.delete_message(chat_id, mes_id)

    if type == 'stc+text':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            '👉 Введите <b>доп текст</b>:',
            kb_send_back(calc_id)
        )

        await state.set(StatsState.send_add_text)
        await state.add_data(
            del_mes_id=new_mes_id, stat_id=calc_id
        )

    if type == 'stc+photo':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            '👉 Отправьте <b>новое фото</b>:',
            kb_send_back(calc_id)
        )

        await state.set(StatsState.send_add_photo)
        await state.add_data(
            del_mes_id=new_mes_id, stat_id=calc_id
        )

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
        calc = calculation.get(calc_id)
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

    if type == 'stc-photo':
        send_data = channel_calc.getByCalc(calc_id)
        if send_data is None:
            return

        calculation.update(calc_id, photo=None)
        await bot.delete_message(chat_id, mes_id)
        await send_confirm_calc_send(bot, call.message, calc_id, True)

    if type == 'stc-text':
        send_data = channel_calc.getByCalc(calc_id)
        if send_data is None:
            return

        calculation.update(calc_id, description=None)
        await bot.delete_message(chat_id, mes_id)
        await send_confirm_calc_send(bot, call.message, calc_id, True)

    if type == 'stc+back':
        await send_confirm_calc_send(bot, call.message, calc_id)

    if type == 'result_cancel':
        calculation.update(
            calc_id, status='CANCEL'
        )

        calc = calculation.get(calc_id)
        if calc is None:
            return

        send_data = channel_calc.getByCalc(calc.id)
        if send_data:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice)

        await delete_message(bot, chat_id, mes_id)
        await send_calculation(bot, call.message, state, user, calc, True)

    if type == 'result_deal':
        calculation.update(
            calc_id, status='DEAL'
        )

        calc = calculation.get(calc_id)
        if calc is None:
            return

        send_data = channel_calc.getByCalc(calc.id)
        if send_data:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice)

        await delete_message(bot, chat_id, mes_id)
        await send_calculation(bot, call.message, state, user, calc, True)

    if type == 'result_wait':
        calculation.update(
            calc_id, status='WAIT'
        )

        calc = calculation.get(calc_id)
        if calc is None:
            return

        send_data = channel_calc.getByCalc(calc.id)
        if send_data:
            tickerInfo = ticker.get_info(calc.tool or '')
            await channel_post.send_calc(calc, send_data, tickerInfo and tickerInfo.indexPrice)

        await delete_message(bot, chat_id, mes_id)
        await send_calculation(bot, call.message, state, user, calc, True)

    if type == 'result_take':
        calc = calculation.get(calc_id)
        if calc is None:
            return

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
        calc = calculation.get(calc_id)
        if calc is None:
            return

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

    if type == 'cancel_at':
        new_mes_id = await edit_message(
            bot, call.message, 'text',
            msg_enter_cancel_at(user.lang),
            kb_cancel_at(user.lang, calc_id)
        )
        await state.set(StatsState.cancel_at)
        await state.add_data(
            calc_id=calc_id,
            del_mes_id=new_mes_id
        )

    if 'cancel_at+' in type:
        _, time = type.split('+')

        if time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        calc = calculation.updateCancelAt(calc_id, time)

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
