from datetime import timedelta
import datetime
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
from CALCULATE.states.calculate import CalculateState, ForexCalcState
from common.calculation import get_count_value_bet
from common.utils import delete_message, edit_message, set_state_data
from common.dt import get_datetime_now, get_str_by_datetime

from data.data import liteDb
from config_global import EN_CHANNEL_ID, PROD, RU_CHANNEL_ID
from config_logger import logger
from Classes import calcService, pay_guard
from db import db
from CALCULATE.common.messages import (
    msg_calculate_change, msg_calculate_delete,
    msg_calculation_deleted, msg_channel_calculation, msg_enter_calc_image,
    msg_enter_open_price, msg_enter_pair, msg_enter_profit_minus,
    msg_enter_save_calc, msg_enter_stop_loss, msg_enter_tool, msg_enter_trading_style,
    msg_frozen, msg_market_stats, msg_enter_profit_sum,
)
from CALCULATE.states import StatsState
from models import MARKETS_TYPE

from ..main.keyboards import kb_main
from ..settings.keyboards import kb_trading_style
from .keyboards import (
    kb_calc_image, kb_calculate_change,
    kb_calculate_delete, kb_channel_url, kb_confirm_channel_post, kb_deal_profit_cancel,
    kb_deal_profit_minus, kb_deal_result, kb_send_calc_time, kb_stats,
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
                        stat_id, -calc_info.risk_value * rate * spot_rate)
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

        liteDb.addSendCalc(stat_id)

        if withoutStop == 'True' or stat.stop_loss == -1:
            liteDb.updateWithoutStopSendCalc(stat_id)
        if isVote == 'False':
            liteDb.updateVoteSendCalc(stat_id)
        if style:
            db.change_calculation_style(stat_id, style)
            liteDb.updateValueSendCalc(stat_id, 'tradingStyle', style)
        if time:
            liteDb.updateValueSendCalc(stat_id, 'time', time)

        bot.edit_message_reply_markup(
            chat_id, mes_id,
            reply_markup=kb_main(user_id, True, stat)
        )
        send_confirm_calc_send(bot, call.message, stat_id, True)

    if type == 'stc+send':
        send_data = liteDb.getSendCalc(stat_id)
        stat = db.get_calculation(stat_id)
        if send_data is None or stat is None:
            return

        photo = send_data.photo

        now = get_datetime_now() + timedelta(hours=3)
        start = datetime.datetime(
            now.year, now.month, now.day, 0, 0, 0, 0
        ) - timedelta(hours=3)
        end = datetime.datetime(
            now.year, now.month, now.day, 0, 0, 0, 0
        ) + timedelta(days=1) - timedelta(hours=3)

        count_show = 1
        send_datas = liteDb.getAllSendCalcs()
        for el in send_datas:
            s = db.get_calculation(el.id)

            if s is not None and s.created_at is not None and s.created_at > start and s.created_at < end:
                count_show += 1

        for i, CHANNEL_ID in enumerate(channels):
            lang = 'ru' if i == 0 else 'en'

            info = get_ticker_info(stat.tool or '')

            # turnover: number;
            # buyRatio: any;
            # sellRatio: any;

            info_show = ''
            if info and info.get('turnover') and info.get('buyRatio') and info.get('sellRatio'):
                oborot = ''
                turnover = info.get('turnover')
                if turnover // (10 ** 9) > 0:
                    oborot = f'{round(turnover // (10**9), 0)}B USDT'
                elif turnover // (10 ** 6) > 0:
                    oborot = f'{round(turnover // (10**6), 0)}M USDT'
                else:
                    oborot = f'{round(turnover, 0)} USDT'

                if lang == 'ru':
                    now_point = 'Сейчас покупают/продают'
                    oborot_point = 'Оборот за 24ч'
                else:
                    now_point = 'Now buy/sell'
                    oborot_point = 'Turnover in 24 hours'

                info_show = f"""
{now_point}: <b>{round(info.get("buyRatio") * 100, 1)}%</b> / <b>{round(info.get("sellRatio") * 100, 1)}%</b>
{oborot_point}: <b>{oborot}</b>
"""

            text = msg_channel_calculation(
                stat, lang, send_data.without_stop, send_data.time or '', count_show
            ) + info_show
            if lang == 'ru':
                description_text = send_data.text
                text += f'\n{description_text}' if description_text is not None else ''

            # votes = liteDb.getVotes(stat_id)
            kb = kb_channel_url(
                lang, stat_id, bot.get_me().username,
            )

            if photo is None:
                bot.send_message(
                    CHANNEL_ID, text,
                    reply_markup=kb
                )
            else:
                bot.send_photo(
                    CHANNEL_ID,
                    photo, text,
                    reply_markup=kb
                )

        bot.delete_message(chat_id, mes_id)
        bot.send_message(chat_id, '✅ Отправлено')
        liteDb.sendSendCalc(stat_id)

        if send_data.is_vote:
            seconds = vote_timeout(stat_id)
            new_mes = bot.send_message(
                chat_id, f'Опрос будет отправлен через {round(seconds, 1)} секунд'
            )
            loading_vote_message_ids[stat_id] = (chat_id, new_mes.id)

        send_main(call.message, bot, user_id, True)

    if type == 'stc+rescreen':
        send_data = liteDb.getSendCalc(stat_id)
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

        text = msg_channel_calculation(stat, 'ru', send_data.without_stop, send_data.time or '') \
            + (f'\n{send_data.text}' if send_data.text is not None else '')

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

        liteDb.updateValueSendCalc(stat_id, 'photo', photo_str)
        bot.delete_message(chat_id, mes_id)

    if type == 'stc+text':
        new_mes_id = edit_message(
            bot, call.message, 'text',
            '👉 Введите <b>доп текст</b>:',
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
        _, value = type.split('=')
        value = None if value == 'none' else value

        liteDb.updateValueSendCalc(stat_id, 'time', value)

        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'stc+stop':
        stat = db.get_calculation(stat_id)
        if stat is None or stat.stop_loss == -1:
            return

        liteDb.updateWithoutStopSendCalc(stat_id)
        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'stc+vote':
        liteDb.updateVoteSendCalc(stat_id)
        send_confirm_calc_send(bot, call.message, stat_id)

    if type == 'stc-photo':
        send_data = liteDb.getSendCalc(stat_id)
        if send_data is None:
            return

        liteDb.updateValueSendCalc(
            stat_id, 'photo', None
        )
        bot.delete_message(chat_id, mes_id)
        send_confirm_calc_send(bot, call.message, stat_id, True)

    if type == 'stc-text':
        send_data = liteDb.getSendCalc(stat_id)
        if send_data is None:
            return

        liteDb.updateValueSendCalc(
            stat_id, 'text', None
        )
        bot.delete_message(chat_id, mes_id)
        send_confirm_calc_send(bot, call.message, stat_id, True)

    if 'vote_up' in type or 'vote_down' in type:
        isUp = 'vote_up' in type
        lang = 'en' if '_en' in type else 'ru'

        is_voted = liteDb.isUserVoted(user_id, stat_id)
        liteDb.delVote(user_id, stat_id)

        if (is_voted == 'up' and isUp) or (is_voted == 'down' and not isUp):
            pass
        else:
            liteDb.userVote(user_id, stat_id, isUp)

        votes = liteDb.getVotes(stat_id)

        bot.edit_message_reply_markup(
            chat_id, mes_id,
            reply_markup=kb_channel_url(
                lang, stat_id, bot.get_me().username,
            )
        )

    bot.answer_callback_query(call.id)


def send_vote(bot: TeleBot, stat_id: int):
    stat = db.get_calculation(stat_id)
    if stat is None:
        return

    for i, CHANNEL_ID in enumerate(channels):
        lang = 'ru' if i == 0 else 'en'
        q = f'👆 {stat.tool or "" or (stat.forex_info.pair if stat.forex_info is not None else "")}'

        if lang == 'ru':
            first = 'В рост'
            second = 'На падение'
        else:
            first = 'Long'
            second = 'Short'

        bot.send_poll(
            CHANNEL_ID, q, [first, second], True
        )

    print(stat_id in loading_vote_message_ids)
    print(loading_vote_message_ids)
    if stat_id in loading_vote_message_ids:
        cur_chat_id, cur_mes_id = loading_vote_message_ids[stat_id]
        bot.edit_message_text(
            '✅ Опрос отправлен', cur_chat_id, cur_mes_id
        )
        loading_vote_message_ids.pop(stat_id)


def registration(bot: TeleBot):
    bot.add_custom_filter(StatsCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=stats_factory.filter()
    )
