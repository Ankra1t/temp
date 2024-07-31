from datetime import timedelta
import os
from random import randint
from time import sleep
from typing import Literal
from telebot import TeleBot
from telebot.types import CallbackQuery

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from AuthRoles import get_ticker_info, vote_timeout
from CALCULATE.callbacks.channel_post.keyboards import kb_channel_calc_result_stop, kb_channel_calc_result_take
from CALCULATE.states.calculate import CalculateState, ForexCalcState
from CALCULATE.states.stats import ChannelCalcState
from common.calculation import get_count_value_bet
from common.utils import delete_message, edit_message, set_state_data
from common.dt import get_datetime_now, get_str_by_datetime

from data.data import liteDb
from config_global import EN_CHANNEL_ID, PROD, RU_CHANNEL_ID
from config_logger import logger
from Classes import calcService, pay_guard
from db import LANGUAGES_TYPE, db
from CALCULATE.common.messages import (
    msg_calculate_change, msg_calculate_delete,
    msg_calculation_deleted, msg_channel_calculation, msg_enter_calc_image,
    msg_enter_open_price, msg_enter_pair, msg_enter_profit_minus,
    msg_enter_save_calc, msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style,
    msg_frozen, msg_market_stats, msg_enter_profit_sum,
)
from CALCULATE.states import StatsState
from models import CHANNEL_STATUS_TYPE, MARKETS_TYPE
from services import channel_calc

from ..main.keyboards import kb_main
from ..settings.keyboards import kb_trading_style
from .keyboards import (
    kb_calc_image, kb_calc_result, kb_calculate_change,
    kb_calculate_delete, kb_confirm_channel_post, kb_deal_profit_cancel,
    kb_deal_profit_minus, kb_deal_result, kb_send_back, kb_send_calc_time, kb_stats,
)
from .filter import stats_factory, StatsCallbackFilter
from ..pages import send_calculation, send_confirm_calc_send, send_freeze, send_main, send_stats

loading_vote_message_ids: dict[int, tuple[int, int]] = {}
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


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = stats_factory.parse(call.data)
    type = callback_data.get('type', '')
    stat_id = int(callback_data.get('stat_id', 0))
    stats_market: MARKETS_TYPE = callback_data.get(
        'stats_market', 'crypto'
    )  # type: ignore

    user_id = call.from_user.id

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "settings_factory" user_tg_id={user_id} type={type} ({stats_market} {stat_id})'
    )

    if 'time+' in type:
        _, time = type.split('+')
        date = get_datetime_now() + timedelta(hours=int(time))

        with bot.retrieve_data(user_id, chat_id) as data:
            market: MARKETS_TYPE | None = data.get('market')

        user_db_id = db.get_user_id_by_tg_id(user_id)
        db.set_user_calc_freeze(user_db_id, date, market)

        bot.edit_message_text(
            msg_frozen(user_id, get_str_by_datetime(date)),
            chat_id, mes_id
        )
        bot.delete_state(user_id, chat_id)

    if 'profit' in type:
        bot.delete_state(user_id, chat_id)
        _, profit = type.split('+')

        if profit == '':
            delete_message(bot, chat_id, mes_id)
            bot.send_message(
                chat_id, msg_enter_save_calc(user_id),
                reply_markup=kb_deal_result(user_id, stat_id)
            )
        else:
            is_cancel = False

            calc_info = db.get_calculation(stat_id)
            if calc_info is None:
                return

            if profit == '-':
                bot.set_state(user_id, StatsState.loss, chat_id)
                set_state_data(bot, user_id, chat_id, {'stat_id': stat_id})
                bot.edit_message_text(
                    msg_enter_profit_minus(user_id),
                    chat_id, mes_id,
                    reply_markup=kb_deal_profit_minus(user_id, stat_id)
                )
            else:
                if 'loss' in profit:
                    rate = float(profit.replace('loss', ''))
                    _, _, spot_rate = get_count_value_bet(calc_info)
                    calcService.set_profit(
                        stat_id, -calc_info.risk_value * rate * spot_rate
                    )
                elif profit != 'cancel':
                    _, _, spot_rate = get_count_value_bet(calc_info)
                    profit_result = calc_info.risk_value * \
                        int(profit) * spot_rate
                    calcService.set_profit(stat_id, profit_result)
                else:
                    is_cancel = True

                calc_info = db.get_calculation(stat_id)
                if calc_info is None:
                    return

                send_calculation(bot, call.message, user_id, calc_info)

                if not is_cancel:
                    send_data = channel_calc.getByCalc(stat_id)
                    if send_data is not None:
                        channel_calc.update(send_data.id, status='FINISH')
                        edit_channel_post(bot, stat_id)
                    send_freeze(bot, call.message, user_id,
                                calc_info.market, True)

    if type == 'sum':
        bot.set_state(user_id, StatsState.sum, chat_id)
        set_state_data(bot, user_id, chat_id, {'stat_id': stat_id})
        bot.edit_message_text(
            msg_enter_profit_sum(user_id),
            chat_id, mes_id,
            reply_markup=kb_deal_profit_cancel(user_id, stat_id)
        )

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if type == 'go_stats':
        send_stats(bot, call.message, user_id)

    if type == 'stats_market':
        stats = calcService.get_stats(user_id, stats_market)
        text = msg_market_stats(user_id, stats_market, stats)

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_stats(user_id, 'market')
        )

    if 'delete_calc' in type:
        if '_yes' in type:
            if db.delete_calculation(stat_id):
                edit_message(
                    bot, call.message, 'text',
                    msg_calculation_deleted(user_id),
                )
                send_main(call.message, bot, user_id, True)
        elif '_no' in type:
            prev_type = call.message.content_type

            if prev_type == 'text':
                text = call.message.html_text or 'err\n'
            else:
                text = call.message.html_caption or 'err\n'

            text = '\n'.join(text.split('\n')[:-1])
            media = call.message.photo[-1].file_id if call.message.photo else None

            is_valid = pay_guard.valid_use_calc(user_id, bot)
            calc_info = db.get_calculation(stat_id)

            edit_message(
                bot, call.message, prev_type,  # type: ignore
                text,
                kb_main(user_id, is_valid, calc_info),
                media
            )
        else:
            prev_type = call.message.content_type

            if prev_type == 'text':
                text = call.message.html_text or 'err\n'
            else:
                text = call.message.html_caption or 'err\n'

            media = call.message.photo[-1].file_id if call.message.photo else None

            edit_message(
                bot, call.message, prev_type,  # type: ignore
                msg_calculate_delete(user_id, text),
                kb_calculate_delete(user_id, stat_id),
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

            edit_message(
                bot, call.message, prev_type,  # type: ignore
                msg_calculate_change(user_id, text),
                kb_calculate_change(user_id, stat_id),
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

            is_valid = pay_guard.valid_use_calc(user_id, bot)
            calc_info = db.get_calculation(stat_id)

            edit_message(
                bot, call.message, prev_type,  # type: ignore
                text,
                kb_main(user_id, is_valid, calc_info),
                media
            )
        elif kind == 'open_price':
            edit_message(
                bot, call.message, 'text',
                msg_enter_open_price(user_id),
                kb_deal_profit_cancel(user_id, stat_id)
            )
            bot.set_state(user_id, CalculateState.open_price, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )
        elif kind == 'stop_loss':
            edit_message(
                bot, call.message, 'text',
                msg_enter_stop_loss(user_id),
                kb_deal_profit_cancel(user_id, stat_id)
            )
            bot.set_state(user_id, CalculateState.stop_loss, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )
        elif kind == 'tool':
            stat = db.get_calculation(stat_id)
            if stat is None:
                return

            if stat.forex_info is not None:
                state = ForexCalcState.pair
                msg = msg_enter_pair(user_id)
            else:
                state = CalculateState.tool
                msg = msg_enter_tool(user_id, stat.market)

            edit_message(
                bot, call.message, 'text', msg,
                kb_deal_profit_cancel(user_id, stat_id)
            )
            bot.set_state(user_id, state, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )
        elif 'style' in kind:
            stc = '+stc' if '_stc' in type else ''
            edit_message(
                bot, call.message, 'text',
                msg_enter_trading_style(user_id),
                kb_trading_style(user_id, 'ch_calc' + stc)
            )
            bot.set_state(user_id, CalculateState.trading_style, chat_id)
            set_state_data(
                bot, user_id, chat_id, {
                    'stat_id': stat_id,
                    'del_mes_id': call.message.id
                }
            )

    if type == 'add_img':
        prev_type = call.message.content_type

        if prev_type == 'text':
            text = call.message.html_text or 'err\n'
        else:
            text = call.message.html_caption or 'err\n'

        text += f'\n\n{msg_enter_calc_image(user_id)}'
        media = call.message.photo[-1].file_id if call.message.photo else None

        delete_message(bot, chat_id, mes_id)
        if prev_type == 'text':
            new_mes = bot.send_message(
                chat_id, text,
                reply_markup=kb_calc_image(user_id, stat_id)
            )
        else:
            new_mes = bot.send_photo(
                chat_id, media, text,
                reply_markup=kb_calc_image(user_id, stat_id)
            )

        bot.set_state(user_id, StatsState.add_image, chat_id)

        set_state_data(bot, user_id, chat_id, {
            'stat_id': stat_id,
            'calc_text': text,
            'calc_media': media,
            'calc_del_mes_id': new_mes.id,
        })

    if type == 'send_to_channels':
        stat = db.get_calculation(stat_id)
        if stat is None:
            return

        withoutStop = liteDb.getSendSettings('withoutStop')
        style = liteDb.getSendSettings('style')
        isVote = liteDb.getSendSettings('isVote')
        time = liteDb.getSendSettings('time')

        send_data = channel_calc.create(stat_id)
        if send_data is None:
            return

        if withoutStop == 'True' or stat.stop_loss == -1:
            channel_calc.update(send_data.id, withoutStop=True)
        if isVote == 'False':
            channel_calc.update(send_data.id, isVote=False)
        if style:
            db.change_calculation_style(stat_id, style)
            channel_calc.update(send_data.id, tradingStyle=style)
        if time:
            channel_calc.update(send_data.id, time=time)

        bot.edit_message_reply_markup(
            chat_id, mes_id,
            reply_markup=kb_calc_result(
                user_id, stat_id
            )
        )
        send_confirm_calc_send(bot, call.message, stat_id, True)

    if type == 'stc+send':
        send_data = channel_calc.getByCalc(stat_id)
        stat = db.get_calculation(stat_id)
        if send_data is None or stat is None:
            return

        photo = send_data.photo

        sent_today = len(channel_calc.getSentToday() or [])

        mesIds: list[int] = []
        for i, CHANNEL_ID in enumerate(channels):
            lang = 'ru' if i == 0 else 'en'

            tickerInfo = get_ticker_info(stat.tool or '')

            weekStat = channel_calc.getWeekStat()
            link = ''
            if weekStat:
                messages = weekStat.get('messages')
                try:
                    weekMesId = messages.get('mesIds', [])[i]
                    link = f'https://t.me/c/{str(CHANNEL_ID).replace("-100", "")}/{weekMesId}'
                except:
                    pass

            text = msg_channel_calculation(
                stat, lang, send_data.withoutStop, send_data.time or '', sent_today + 1,
                tickerInfo=tickerInfo or None,
                description=send_data.text if lang == 'ru' else None,
                week_stat_link=link,
                try_link=f'https://t.me/{bot.get_me().username}?start=calc_{stat_id}'
            )

            if photo is None:
                new_mes = bot.send_message(
                    CHANNEL_ID, text,
                )
            else:
                new_mes = bot.send_photo(
                    CHANNEL_ID,
                    photo, text,
                )

            mesIds.append(new_mes.id)

        bot.delete_message(chat_id, mes_id)
        bot.send_message(chat_id, '✅ Отправлено')

        channel_calc.update(
            send_data.id,
            sent=True,
            messages={
                'chIds': [str(el) for el in channels],
                'mesIds': [str(el) for el in mesIds],
                'langs': ['ru', 'en'],
            }
        )

        send_week_stats(bot)

        if send_data.isVote:
            seconds = vote_timeout(stat_id)
            new_mes = bot.send_message(
                chat_id, f'Опрос будет отправлен через {round(seconds, 1)} секунд'
            )
            loading_vote_message_ids[stat_id] = (chat_id, new_mes.id)

        send_main(call.message, bot, user_id, True)

    if type == 'stc+rescreen':
        send_data = channel_calc.getByCalc(stat_id)
        stat = db.get_calculation(stat_id)
        if stat is None or send_data is None:
            return

        new_mes = bot.send_message(
            chat_id, 'Генерация изображения...',
        )

        try:
            file_path = createScreen(
                (stat.tool or '').replace('/', '').upper(),
                '1h', 'candles', 6
            )
        except Exception as e:
            print(e)
            file_path = None

        text = msg_channel_calculation(
            stat, 'ru', send_data.withoutStop, send_data.time or '',
            description=send_data.text
        )

        if file_path is None:
            bot.edit_message_text(
                'Ошибка генерации фото', new_mes.chat.id, new_mes.id,
            )

            main_mes = bot.send_message(
                chat_id, text,
                reply_markup=kb_confirm_channel_post(
                    stat_id
                )
            )
        else:
            bot.delete_message(new_mes.chat.id, new_mes.id)

            with open(file_path, 'rb') as photo:
                main_mes = bot.send_photo(
                    chat_id, photo, text,
                    reply_markup=kb_confirm_channel_post(
                        stat_id
                    )
                )
            os.remove(file_path)

        photo_str = None
        if main_mes.photo is not None and len(main_mes.photo) > 0:
            photo_str = main_mes.photo[-1].file_id

        channel_calc.update(send_data.id, photo=photo_str)
        bot.delete_message(chat_id, mes_id)

    if type == 'stc+text':
        new_mes_id = edit_message(
            bot, call.message, 'text',
            '👉 Введите <b>доп текст</b>:',
            kb_send_back(stat_id)
        )

        bot.set_state(user_id, StatsState.send_add_text, chat_id)
        set_state_data(
            bot, user_id, chat_id, {
                'del_mes_id': new_mes_id, 'stat_id': stat_id
            }
        )

    if type == 'stc+photo':
        new_mes_id = edit_message(
            bot, call.message, 'text',
            '👉 Отправьте <b>новое фото</b>:',
            kb_send_back(stat_id)
        )

        bot.set_state(user_id, StatsState.send_add_photo, chat_id)
        set_state_data(
            bot, user_id, chat_id, {
                'del_mes_id': new_mes_id, 'stat_id': stat_id
            }
        )

    if type == 'stc+time':
        edit_message(
            bot, call.message, 'text',
            '👉 Выберите тип периода:',
            kb_send_calc_time(stat_id)
        )

    if 'stc+time=' in type:
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is None:
            return

        _, value = type.split('=')
        value = None if value == 'none' else value

        channel_calc.update(send_data.id, time=value)
        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'stc+stop':
        stat = db.get_calculation(stat_id)
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is None or stat is None or stat.stop_loss == -1:
            return

        channel_calc.update(
            send_data.id, withoutStop=not send_data.withoutStop)
        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'stc+vote':
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is None:
            return

        channel_calc.update(send_data.id, isVote=not send_data.isVote)
        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'stc-photo':
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is None:
            return

        channel_calc.update(send_data.id, photo=None)
        bot.delete_message(chat_id, mes_id)
        send_confirm_calc_send(bot, call.message, stat_id, True)

    if type == 'stc-text':
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is None:
            return

        channel_calc.update(send_data.id, text=None)
        bot.delete_message(chat_id, mes_id)
        send_confirm_calc_send(bot, call.message, stat_id, True)

    if type == 'stc+back':
        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'result_cancel':
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            channel_calc.update(
                send_data.id, status='CANCEL'
            )

        edit_channel_post(bot, stat_id)

        calc = db.get_calculation(stat_id)
        if calc is None:
            return

        delete_message(bot, chat_id, mes_id)
        send_calculation(bot, call.message, user_id, calc, True)

    if type == 'result_deal':
        send_data = channel_calc.getByCalc(stat_id)
        if send_data is not None:
            channel_calc.update(send_data.id, status='DEAL')

        edit_channel_post(bot, stat_id)

        calc = db.get_calculation(stat_id)
        if calc is None:
            return

        delete_message(bot, chat_id, mes_id)
        send_calculation(bot, call.message, user_id, calc, True)

    if type == 'result_take':
        calc = db.get_calculation(stat_id)
        if calc is None:
            return

        bot.edit_message_reply_markup(
            chat_id, mes_id, reply_markup=kb_channel_calc_result_take(
                calc.tp_ratio, stat_id, True
            )
        )
        bot.set_state(user_id, ChannelCalcState.loss, chat_id)
        set_state_data(
            bot, user_id, chat_id, {
                'del_mes_id': mes_id,
                'stat_id': stat_id,
                'is_calc': True,
                'type': 'take'
            }
        )

    if type == 'result_stop':
        calc = db.get_calculation(stat_id)
        if calc is None:
            return

        bot.edit_message_reply_markup(
            chat_id, mes_id, reply_markup=kb_channel_calc_result_stop(
                stat_id, True
            )
        )
        bot.set_state(user_id, ChannelCalcState.loss, chat_id)
        set_state_data(
            bot, user_id, chat_id, {
                'del_mes_id': mes_id,
                'stat_id': stat_id,
                'is_calc': True,
                'type': 'stop'
            }
        )

    bot.answer_callback_query(call.id)


def send_vote(bot: TeleBot, stat_id: int):
    stat = db.get_calculation(stat_id)
    if stat is None:
        return

    rand = randint(1, 3)
    for i, CHANNEL_ID in enumerate(channels):
        lang = 'ru' if i == 0 else 'en'

        if rand == 1:
            q = f'👆 {stat.tool or "" or (stat.forex_info.pair if stat.forex_info is not None else "")}'

            if lang == 'ru':
                ans = ['В рост', 'На падение']
            else:
                ans = ['Long', 'Short']
        elif rand == 2:
            if lang == 'ru':
                q = '👆 Войдете в сделку?'
                ans = ['Да', 'Нет', 'Подумаю']
            else:
                q = '👆 Will be in deal?'
                ans = ['Yes', 'No', 'Thinking']
        else:
            if lang == 'ru':
                q = '👆 Нравится график?'
                ans = ['Да', 'Нет']
            else:
                q = '👆 Do you like grafic?'
                ans = ['Yes', 'No']

        bot.send_poll(
            CHANNEL_ID, q, ans, True
        )

    if stat_id in loading_vote_message_ids:
        cur_chat_id, cur_mes_id = loading_vote_message_ids[stat_id]
        bot.edit_message_text(
            '✅ Опрос отправлен', cur_chat_id, cur_mes_id
        )
        loading_vote_message_ids.pop(stat_id)


def send_week_stats(bot: TeleBot, calcId: int | None = None, is_new_week=False):
    texts = {
        'ru': {
            'title': '⚡️ <b>Результаты на эту неделю</b>',

            'title2': '⚡️ Результаты',
            'from': 'с',
            'to': 'по',

            'stop': 'стоп',
            'count to': 'к',

            'DEAL': 'В сделке',
            'CANCEL': 'Отменён',

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
            'count to': 'to',

            'DEAL': 'In deal',
            'CANCEL': 'Cancel',

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

    if is_new_week:
        mes_ids: list[int] = []

        for i, CHANNEL_ID in enumerate(channels):
            lang = 'ru' if i == 0 else 'en'

            msg = texts[lang]["title"]

            mes = bot.send_message(
                CHANNEL_ID, msg,
            )
            bot.pin_chat_message(CHANNEL_ID, mes.id)
            mes_ids.append(mes.id)

        channel_calc.createWeekStat(list(channels), mes_ids, ['ru', 'en'])

    data = channel_calc.getWeekStat(calcId)
    if data is None:
        return

    ch_mes: dict = data.get('messages')
    chIds: list[str] = ch_mes.get('chIds', [])
    mesIds: list[str] = ch_mes.get('mesIds', [])
    langs: list[LANGUAGES_TYPE] = ch_mes.get('langs', [])

    startDate = data.get('startDate')
    endDate = data.get('endDate')

    values: list[dict] = data.get('values')

    for i, CHANNEL_ID in enumerate(chIds):
        lang = langs[i]

        msg = f"<b>{texts[lang]['title2']} {texts[lang]['from']} {startDate} {texts[lang]['to']} {endDate}</b>"

        all_tp_count = 0
        all_sl_count = 0

        long_count = 0
        short_count = 0

        all_success_count = 0
        all_fail_count = 0

        tool_counts: dict[str, int] = {}

        for valueDate_i, valueDate in enumerate(values):
            date_msg = ''

            tp_count = 0
            sl_count = 0

            success_count = 0
            fail_count = 0

            canceled = ''

            for value_i, value in enumerate(valueDate.get('calcs', [])):
                status: CHANNEL_STATUS_TYPE = value.get('status', 'WAIT')
                if status == 'WAIT':
                    continue

                valueCount = value.get('valueCount')
                openPrice = value.get('openPrice')
                closePrice = value.get('closePrice')

                calc_messages = value.get('messages')

                mesId = None
                if calc_messages is not None:
                    calc_chIds: list[str] = calc_messages.get('chIds', [])
                    calc_mesIds: list[str] = calc_messages.get('mesIds', [])
                    try:
                        mes_i = calc_chIds.index(CHANNEL_ID)
                        mesId = calc_mesIds[mes_i]
                    except:
                        pass

                tp_sl = ''
                if valueCount is None:
                    tp_sl = texts[lang][status]
                elif valueCount == 0:
                    tp_sl = texts[lang]['breakeven']
                elif valueCount > 0:
                    tp_sl = f'{valueCount} {texts[lang]["count to"]} 1'
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

                link_start = f'<a href="https://t.me/c/{CHANNEL_ID.replace("-100", "")}/{mesId}">' if mesId is not None else ''
                link_end = '</a>' if mesId is not None else ''

                tool = value.get("tool")
                tool_num = ''
                if tool not in tool_counts:
                    tool_counts[tool] = 1
                else:
                    tool_counts[tool] += 1
                    tool_num = f'({tool_counts[tool]})'

                if status == 'CANCEL':
                    if canceled != '':
                        canceled += ', '
                    canceled += f'{link_start}<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b>{link_end}'
                else:
                    date_msg += f'\n{value_i + 1}. {link_start}<b>{(tool or "-").replace("/USDT", "")}{tool_num}</b>{link_end} - {tp_sl}'

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

            all_success_count += success_count
            all_fail_count += fail_count
            all_tp_count += tp_count
            all_sl_count += sl_count

        msg += f'\n_________________________________'

        tp_sl_result = round(all_tp_count - all_sl_count, 1)

        tp_sl_show = ''
        if tp_sl_result > 0:
            tp_sl_show = f'{texts[lang]["tp"]}'
        else:
            tp_sl_show = f'{texts[lang]["sl"]}'

        if all_tp_count == 0 and all_sl_count == 0:
            if lang == 'ru':
                msg += f'\n\nОжидаются ближайшие сделки'
            else:
                msg += f'\n\nUpcoming deals are expected'

        if all_tp_count != 0 or all_sl_count != 0:
            msg += f'\n\n<b>{texts[lang]["result"]}</b>: '
            if tp_sl_result == 0:
                msg += f'{texts[lang]["breakeven"]}'
            else:
                msg += f'{"+" if tp_sl_result > 0 else "-"}{abs(tp_sl_result)} {tp_sl_show}'
            msg += '\n'

        if long_count != 0 or short_count != 0:
            if long_count != 0:
                msg += f'<b>{texts[lang]["long"]}</b>: {long_count}'
            if long_count != 0 and short_count != 0:
                msg += ' / '
            if short_count != 0:
                msg += f'<b>{texts[lang]["short"]}</b>: {short_count}'

        if all_success_count != 0 or all_fail_count != 0:
            msg += f'\n<b>{texts[lang]["success"]}</b>: {round((all_success_count * 100) / (all_success_count + all_fail_count))} %'

        try:
            bot.edit_message_text(
                msg, CHANNEL_ID, int(mesIds[i])
            )
        except:
            pass


def edit_channel_post(bot: TeleBot, calc_id: int):
    calc = db.get_calculation(calc_id)
    send_data = channel_calc.getByCalc(calc_id)
    messages = channel_calc.getSentMessagesByCalc(calc_id)
    if messages is None or calc is None or send_data is None:
        return

    for i, el in enumerate(messages.chIds):
        link = ''
        # and (send_data.status == 'DEAL' or send_data.status == 'FINISH')
        if messages.messages:
            try:
                weekMesId = messages.messages.get('mesIds', [])[i]
                link = f'https://t.me/c/{el.replace("-100", "")}/{weekMesId}'
            except:
                pass

        msg = msg_channel_calculation(
            calc, messages.langs[i], True, send_data.time or '',
            messages.mesNum or -1, None, send_data.text, link,
            send_data.status, messages.date,
            try_link=f'https://t.me/{bot.get_me().username}?start=calc_{calc_id}'
        )

        try:
            if send_data.photo is None:
                bot.edit_message_text(
                    msg, el, int(messages.mesIds[i]),
                )
            else:
                bot.edit_message_caption(
                    msg, el, int(messages.mesIds[i]),
                )
        except Exception as e:
            print(e)

    send_week_stats(bot, calc_id)


def registration(bot: TeleBot):
    bot.add_custom_filter(StatsCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=stats_factory.filter()
    )
