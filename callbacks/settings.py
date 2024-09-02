from typing import Any
from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from NOTIFIER import notifier
from config_logger import logger
from db import db
from data.data import liteDb
from Classes import text_editor
from models import LANGUAGES
from services import auth, calculation

from states.settings import FirstCalcState, SettingsState

from messages.common import msg_success_edit
from messages.enter import msg_choose_lang, msg_enter_atr_percent, msg_enter_bars, msg_enter_bars_count, msg_enter_currency, msg_enter_day_risk, msg_enter_deposit, msg_enter_market, msg_enter_risk_percent, msg_enter_round_count, msg_enter_splitting, msg_enter_summury_profit_type, msg_enter_take_profit, msg_enter_trading_style, msg_enter_trading_type
from messages.settings import msg_choose_exchange_level, msg_confirm_reset, msg_enter_exchange, msg_settings_change_base, msg_settings_change_market
from messages.main import msg_success_base_set, msg_welcome

from common.calc_step import choose_calculate_step
from common.utils import delete_message, get_lang, get_print_float, set_state_data

from keyboards.main import kb_first_calc
from keyboards.settings import (
    settings_factory, SettingsCallbackFilter,
    kb_atr_bars, kb_atr_bars_count, kb_change_base, kb_change_currency, kb_change_market, kb_choose_exchange_level,
    kb_choose_lang, kb_base_cancel, kb_enter_exchange, kb_round_count, kb_settings_confirm,
    kb_splitting, kb_splitting_last, kb_stop_type_cancel, kb_trading_style,
    kb_summury_profit_type, kb_take_profit, kb_deposit_cancel, kb_trading_type
)

from pages.calculate import (
    send_atr_settings, send_calculation, send_confirm_calc_send, send_dop_settings, send_exchange_settings, send_main,
    send_maker_or_taker, send_settings, send_stop_settings, send_summury_profit_settings, send_trading_style_settings,
    send_user_deposit
)


async def _settings_callback_handler(call: CallbackQuery, bot: AsyncTeleBot):
    callback_data = settings_factory.parse(call.data)
    type = callback_data.get('type', '')

    trading_value = callback_data.get('style', '')
    summury_type = callback_data.get('sum_type', '')
    take_profit_add = callback_data.get('tp', '')
    add_count = callback_data.get('count', '')

    user_id = call.from_user.id
    lang = get_lang(user_id)
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "settings_factory" user_tg_id={user_id} type={type} ({trading_value} {summury_type} {take_profit_add} {add_count})')

    if type == 'set_deposit':
        u_base = db.get_calc_user_settings(user_db_id)

        current_value = ''
        if u_base is not None and u_base.deposit is not None:
            current_value = f'{get_print_float(u_base.deposit, 2)} {u_base.currency or ""}'

        await bot.edit_message_text(
            msg_enter_deposit(lang, current_value),
            chat_id, mes_id,
            reply_markup=kb_deposit_cancel(lang)
        )
        await bot.set_state(user_id, SettingsState.deposit, chat_id)

    if type == 'set_risk_percent':
        await bot.edit_message_text(
            msg_enter_risk_percent(lang),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(lang)
        )
        await bot.set_state(user_id, SettingsState.risk_percent, chat_id)

    if type == 'set_day_risk':
        await bot.edit_message_text(
            msg_enter_day_risk(lang),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(lang)
        )
        await bot.set_state(user_id, SettingsState.day_risk, chat_id)

    if type == 'set_round_count':
        if add_count == '':
            u_base = db.get_calc_user_settings(user_db_id, is_create=False)

            current_value = -1
            if u_base is not None:
                current_value = u_base.round_count or current_value

            await bot.edit_message_text(
                msg_enter_round_count(lang),
                chat_id, mes_id,
                reply_markup=kb_round_count(lang, current_value)
            )
            await bot.set_state(user_id, SettingsState.round_count, chat_id)
        else:
            add_count = int(add_count)
            db.set_user_round_count(user_db_id, min(max(add_count, 0), 5))
            await send_user_deposit(bot, call.message, user_id)

    if type == 'trading_style':
        await send_trading_style_settings(bot, call.message, user_id)

    if 'ss_' in type:
        if trading_value == '':
            await bot.set_state(user_id, SettingsState.trading_style, chat_id)
            await bot.edit_message_text(
                msg_enter_trading_style(lang),
                chat_id, mes_id,
                reply_markup=kb_trading_style(lang)
            )
        else:
            value = trading_value.lower()
            if value == '**off**':
                value = None

            if 'ch_calc' in type:
                async with bot.retrieve_data(user_id, chat_id) as data:
                    stat_id = data.get('stat_id')

                calc_info = calculation.get(stat_id)
                if calc_info is None:
                    return

                if value != '**cancel**':
                    db.change_calculation_style(stat_id, value)
                    calc_info.tradingStyle = value

                if '+stc' in type:
                    await send_confirm_calc_send(bot, call.message, stat_id)
                else:
                    await send_calculation(
                        bot, call.message,
                        user_id, calc_info
                    )
                await bot.delete_state(user_id, chat_id)

            elif 'calc' in type:
                value = value or False

                await set_state_data(
                    bot, user_id, chat_id, {
                        'trading_style': value
                    }
                )
                await choose_calculate_step(
                    bot, user_id, call.message, True, last_value='trading_style'
                )

            else:
                db.set_user_trading_style(user_db_id, value)

                if 'welcome' in type:
                    await bot.edit_message_text(
                        msg_success_base_set(lang), chat_id, mes_id
                    )
                else:
                    await bot.edit_message_text(
                        msg_success_edit(lang), chat_id, mes_id
                    )

                await send_trading_style_settings(bot, call.message, user_id)

    if type == 'switch_style_change':
        liteDb.switchStyleChange(user_id)
        await send_trading_style_settings(bot, call.message, user_id)

    if 'set_currency' in type:
        if type == 'set_currency':
            await bot.edit_message_text(
                msg_enter_currency(lang),
                chat_id, mes_id,
                reply_markup=kb_change_currency(lang)
            )
            await bot.set_state(user_id, SettingsState.currency, chat_id)
        else:
            _, currency = type.split('+')

            if 'welcome' in type:
                db.set_user_currency(user_db_id, currency.upper())
                await bot.set_state(user_id, FirstCalcState.deposit, chat_id)
                await bot.edit_message_text(
                    msg_enter_deposit(lang), chat_id, mes_id
                )
            else:
                if 'calc' in type:
                    await set_state_data(
                        bot, user_id, chat_id, {
                            'currency': currency.upper()
                        }
                    )
                    await choose_calculate_step(
                        bot, user_id, call.message, True, last_value='currency'
                    )
                else:
                    db.set_user_currency(user_db_id, currency.upper())
                    await bot.edit_message_text(
                        msg_success_edit(lang), chat_id, mes_id
                    )
                    await send_user_deposit(bot, call.message, user_id, True)

    if 'choose_lang' in type:
        is_edit_lang = False

        for langg in LANGUAGES:
            if f'_{langg}' in type:
                is_edit_lang = True
                db.set_user_lang(user_db_id, langg)

                if 'first' in type:
                    liteDb.setFirstLang(user_id)

                    await bot.edit_message_text(
                        msg_welcome(langg), chat_id, mes_id,
                        reply_markup=kb_first_calc(langg),
                        disable_web_page_preview=True
                    )

                    sent_messages = auth.getUserNotificationMessages(
                        user_db_id
                    )

                    if sent_messages:
                        await notifier.change_user_choosed_lang(
                            user_db_id, langg, sent_messages
                        )
                else:
                    await send_settings(bot, call.message, user_id)

        if not is_edit_lang:
            await bot.edit_message_text(
                msg_choose_lang(lang),
                chat_id, mes_id,
                reply_markup=kb_choose_lang(lang)
            )

    if type == 'go_main':
        await send_main(call.message, bot, user_id)

    if type == 'go_settings':
        await send_settings(bot, call.message, user_id)

    if type == 'go_change_base':
        await bot.edit_message_text(
            msg_settings_change_base(lang),
            chat_id, mes_id,
            reply_markup=kb_change_base(lang)
        )

    if 'market' in type:
        type_list = type.split('_')

        if len(type_list) == 1:
            lang = get_lang(user_id)
            text = text_editor.get_text(user_id, 'settings_market')
            media_id = text_editor.get_media_id(user_id, 'settings_market')

            market = db.get_user_current_market(user_db_id)

            kb = kb_change_market(lang, '', market)

            if lang == 'ru' and media_id != '':
                await delete_message(bot, chat_id, mes_id)

                await bot.send_animation(
                    chat_id, media_id or 'CgACAgIAAxkBAAIBK2aFbYeuDAM1Re96gn3ps4JUeVy3AAJaSQACYZzRSaXZeP8tB3j8NQQ',
                    caption=text,
                    reply_markup=kb
                )
            else:
                await bot.edit_message_text(
                    msg_settings_change_market(lang),
                    chat_id, mes_id,
                    reply_markup=kb
                )
        else:
            market: Any = type_list[1]
            try:
                action = type_list[2]
            except:
                action = ''

            db.set_calculator_user_market(user_db_id, market)

            if action == 'first':
                db.create_tg_user_settings(user_db_id, market)
                liteDb.setUserFirstMarket(user_id, market)

                if market == 'RF':
                    currency = 'RUB'
                elif market == 'USA':
                    currency = 'USD'
                elif market == 'crypto':
                    currency = 'USDT'
                else:
                    currency = ''

                if currency == '':
                    await bot.edit_message_text(
                        msg_enter_currency(lang), chat_id, mes_id,
                        reply_markup=kb_change_currency(lang, 'welcome')
                    )
                    await bot.set_state(user_id, SettingsState.currency, chat_id)
                    await set_state_data(
                        bot, user_id, chat_id,
                        {'action': 'welcome'}
                    )
                else:
                    db.set_user_currency(user_db_id, currency)
                    await bot.set_state(user_id, FirstCalcState.deposit, chat_id)
                    await bot.edit_message_text(
                        msg_enter_deposit(lang), chat_id, mes_id
                    )
            else:
                await send_settings(bot, call.message, user_id)

    if type == 'first_dep':
        await bot.set_state(user_id, FirstCalcState.deposit, chat_id)
        await bot.edit_message_text(
            msg_enter_deposit(lang), chat_id, mes_id
        )

    if 'welcome_confirm' in type:
        if 'no' in type:
            await send_main(call.message, bot, user_id, True)
        if 'yes' in type:
            # Переход к логике ввода базовых значений
            await bot.edit_message_text(
                msg_enter_currency(lang), chat_id, mes_id,
                reply_markup=kb_change_currency(lang, 'welcome')
            )
            await bot.set_state(user_id, SettingsState.currency, chat_id)
            await set_state_data(bot, user_id, chat_id, {'action': 'welcome'})

    if 'reset' in type:
        if '_yes' in type:
            try:
                # Сброс настроек калькулятора до начальных
                db.reset_user_settings(user_db_id)
                await send_settings(bot, call.message, user_id)
            except:
                # Нет изменений - ничего не изменяется
                pass
        elif '_no' in type:
            await send_settings(bot, call.message, user_id)
        else:
            await bot.edit_message_text(
                msg_confirm_reset(lang), chat_id, mes_id,
                reply_markup=kb_settings_confirm(lang, 'reset')
            )

    if 'deposit_update' in type:
        if '_on' in type:
            db.set_user_updating_deposit(user_db_id, True)
        elif '_off' in type:
            db.set_user_updating_deposit(user_db_id, False)

        await send_user_deposit(bot, call.message, user_id)

    if type == 'summury_profit':
        # Вывод страницы с "Выводом профита" и его изменением
        await send_summury_profit_settings(bot, call.message, user_id)

    if type == 'change_summury_profit':
        # Если summury_type не задан, то выводим страницу для выбора типа
        # Два типа: с разделением и без
        if summury_type == '':
            await bot.edit_message_text(
                msg_enter_summury_profit_type(lang),
                chat_id, mes_id,
                reply_markup=kb_summury_profit_type(lang)
            )

            # Стираем state и задаем новый
            # State ничего не отслеживает, задается для сохранения данных
            await bot.delete_state(user_id, chat_id)
            await bot.set_state(user_id, SettingsState.summury_profit, chat_id)
        else:
            async with bot.retrieve_data(user_id, chat_id) as data:
                # Получаем текущие данные
                current_tp_ratio: list[int] = data.get('take_profit', [])
                current_split: list[float] = data.get('split', [])

                # Проверяем задано ли кол-во на добавление/удаление
                if add_count != '':
                    add_count = int(add_count)

                    # Если число меньше нуля - удаляем это кол-во из массивов
                    # Для случая, если пользователь нажимает на кнопку "Назад"
                    if add_count < 0:
                        current_tp_ratio = current_tp_ratio[:add_count]
                        current_split = current_split[:add_count]
                    else:
                        # Ищем текущий максимальный тейк-профит
                        max_tp = max(current_tp_ratio)

                        # Разделяем остатки процентов на кол-во добавляемых
                        percents_sum = sum(current_split)
                        if abs(percents_sum - 100) < 0.1:
                            percents_sum = 100
                        new_percent = round(
                            (100 - percents_sum) / add_count, 2
                        )

                        # Добавляем значения
                        for i in range(1, add_count + 1):
                            current_tp_ratio.append(max_tp + i)
                            current_split.append(new_percent)

                # Добавление тейк-профита, если задано
                if take_profit_add != '':
                    tp_temp = int(take_profit_add)
                    if tp_temp in current_tp_ratio:
                        current_tp_ratio.remove(tp_temp)
                    else:
                        current_tp_ratio.append(tp_temp)

                # Сохраняем данные в state
                data['take_profit'] = current_tp_ratio
                data['split'] = current_split

            # Далее выводим страницу по summury_type
            if summury_type == 'default':
                await bot.edit_message_text(
                    msg_enter_take_profit(lang, current_tp_ratio),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(lang, current_tp_ratio)
                )
            elif summury_type == 'splitting':
                if add_count != '':
                    # Если было добавлено больше одного элемента
                    kb = kb_splitting(
                        lang, current_tp_ratio, current_split, add_count
                    )
                elif len(current_tp_ratio) == len(current_split):
                    # Если кол-во тейк-профитов и процентов одинаково,
                    # то даем выбрать следующий тейк-профит
                    kb = kb_splitting(
                        lang, current_tp_ratio, current_split
                    )
                else:
                    # Иначе даем ввести процент для последнего выбранного тейк-профита
                    kb = None
                    await bot.set_state(user_id, SettingsState.splitting, chat_id)
                await bot.edit_message_text(
                    msg_enter_splitting(
                        lang, current_tp_ratio, current_split
                    ),
                    chat_id, mes_id,
                    reply_markup=kb
                )

    if 'save' in type:
        async with bot.retrieve_data(user_id, chat_id) as data:
            current_tp_ratio: list[int] = data.get('take_profit', [])
            current_split: list[float] = data.get('split', [])

        # При сохранении тейк-профита без разделения
        if type == 'tp_save':
            current_tp_ratio.sort()
            db.set_calculator_tp_ratio(user_db_id, current_tp_ratio)
            db.set_user_split_values(user_db_id, None)

        # При сохранении вывода с разделением
        if type == 'splitting_save':
            # Сортируем по возрастанию тейк-профитов
            sorted_tp, sorted_split = zip(
                *sorted(zip(current_tp_ratio, current_split))
            )
            sorted_tp = list(sorted_tp)
            sorted_split = list(sorted_split)

            db.set_calculator_tp_ratio(user_db_id, sorted_tp)
            db.set_user_split_values(user_db_id, sorted_split)

        # Выводим сообщения
        await bot.edit_message_text(msg_success_edit(lang), chat_id, mes_id)
        await send_summury_profit_settings(bot, call.message, user_id, True)

    if type == 'splitting_last':
        async with bot.retrieve_data(user_id, chat_id) as data:
            current_tp_ratio: list[int] = data.get('take_profit', [])
            current_split: list[float] = data.get('split', [])

        await bot.edit_message_text(
            msg_enter_splitting(
                lang, current_tp_ratio, current_split, True
            ),
            chat_id, mes_id,
            reply_markup=kb_splitting_last(lang)
        )

    if 'trading_type' in type:
        if trading_value == '':
            await bot.edit_message_text(
                msg_enter_trading_type(lang), chat_id, mes_id,
                reply_markup=kb_trading_type(lang)
            )
        else:
            db.set_user_trading_type(user_db_id, trading_value)  # type: ignore
            await send_settings(bot, call.message, user_id)

    if type == 'calc_output':
        cur_calc_output = db.get_user_calc_output(user_db_id)
        db.set_user_calc_output(
            user_db_id,
            'text' if cur_calc_output == 'photo' else 'photo'
        )
        await send_dop_settings(bot, call.message, user_id)

    if type == 'set_first_settings':
        await bot.edit_message_text(
            msg_enter_market(lang), chat_id, mes_id,
            reply_markup=kb_change_market(lang, 'first')
        )

    if type == 'set_risk_update':
        liteDb.reverseRiskUpdate(user_id)
        await send_dop_settings(bot, call.message, user_id)

    if type == 'exchange':
        exchange = liteDb.getUserExchange(user_id)

        if exchange is None:
            await bot.edit_message_text(
                msg_enter_exchange(lang),
                chat_id, mes_id,
                reply_markup=kb_enter_exchange(lang, is_first=True)
            )
            await bot.set_state(user_id, SettingsState.exchange, chat_id)
            await set_state_data(bot, user_id, chat_id, {'del_mes_id': mes_id})
        else:
            await send_exchange_settings(bot, call.message, user_id)

    if 'set_exchange' in type:
        if type == 'set_exchange':
            await bot.edit_message_text(
                msg_enter_exchange(lang),
                chat_id, mes_id,
                reply_markup=kb_enter_exchange(lang)
            )
            await bot.set_state(user_id, SettingsState.exchange, chat_id)
            await set_state_data(bot, user_id, chat_id, {'del_mes_id': mes_id})
        else:
            exchange_value = type.split('++')[1]

            exchange = liteDb.getExchangeByName(exchange_value)
            if exchange is None:
                return

            if len(exchange.fees) != 0:
                await bot.edit_message_text(
                    msg_choose_exchange_level(lang, exchange.fees),
                    chat_id, mes_id,
                    reply_markup=kb_choose_exchange_level(
                        lang, exchange.name, [el[0] for el in exchange.fees]
                    )
                )
            else:
                await send_maker_or_taker(
                    bot, call.message, chat_id,
                    (exchange.name, exchange.maker_fee, exchange.taker_fee)
                )

    if 'set_ex_lvl' in type:
        _, name, lvl_name = type.split('++')

        exchange = liteDb.getExchangeByName(name)
        if exchange is None:
            return

        maker_fee, taker_fee = 0, 0
        for fee in exchange.fees:
            if fee[0] == lvl_name:
                maker_fee, taker_fee = fee[1], fee[2]
                break

        await send_maker_or_taker(
            bot, call.message, user_id,
            (exchange.name, maker_fee, taker_fee)
        )

    if type == 'set_fee':
        user_exchange = liteDb.getUserExchange(user_id)

        if user_exchange is None:
            return

        exchange = liteDb.getExchangeByName(user_exchange[0])
        if exchange is None:
            return

        if len(exchange.fees) != 0:
            await bot.edit_message_text(
                msg_choose_exchange_level(lang, exchange.fees),
                chat_id, mes_id,
                reply_markup=kb_choose_exchange_level(
                    lang, exchange.name, [el[0] for el in exchange.fees]
                )
            )
        else:
            await send_maker_or_taker(
                bot, call.message, chat_id,
                (exchange.name, exchange.maker_fee, exchange.taker_fee)
            )

        await bot.set_state(user_id, SettingsState.fee, chat_id)
        await set_state_data(bot, user_id, chat_id, {'del_mes_id': mes_id})

    if 'set_ex_fee' in type:
        _, name, value = type.split('++')
        liteDb.setUserExchange(user_id, (name, float(value)))
        await send_exchange_settings(bot, call.message, user_id)

    if type == 'dop':
        await send_dop_settings(bot, call.message, user_id)

    if 'set_stop' in type:
        _, new_stop_type = type.split('+')

        db.set_user_from_deposit(user_db_id, False)
        if new_stop_type == 'atr_percent':
            await bot.edit_message_text(
                msg_enter_atr_percent(lang), chat_id, mes_id,
                reply_markup=kb_stop_type_cancel(lang)
            )
            await bot.set_state(user_id, SettingsState.atr_percent, chat_id)
        else:
            liteDb.setUserStop(user_id, new_stop_type)

            if new_stop_type == 'atr':
                await send_atr_settings(bot, call.message, user_id)
            else:
                try:
                   await  send_stop_settings(bot, call.message, user_id)
                except:
                    pass

    if type == 'stop_settings':
        await send_stop_settings(bot, call.message, user_id)

    if type == 'change_fr_dp':
        u_base = db.get_calc_user_settings(user_db_id)
        curr = False
        if u_base is not None:
            curr = u_base.is_from_deposit

        db.set_user_from_deposit(user_db_id, not curr)
        await send_stop_settings(bot, call.message, user_id)

    if type == 'atr_settings':
        await send_atr_settings(bot, call.message, user_id)

    if type == 'atr_auto':
        atr_settings = liteDb.getUserAtrSettings(user_id)
        if atr_settings[0]:
            return

        liteDb.setUserAtrSettings(
            user_id, (not atr_settings[0], atr_settings[1])
        )
        await send_atr_settings(bot, call.message, user_id)

    if type == 'atr_self':
        atr_settings = liteDb.getUserAtrSettings(user_id)
        if not atr_settings[0]:
            return

        liteDb.setUserAtrSettings(
            user_id, (not atr_settings[0], atr_settings[1])
        )
        await send_atr_settings(bot, call.message, user_id)

    if type == 'atr_bars':
        await bot.edit_message_text(
            msg_enter_bars(lang), chat_id, mes_id,
            reply_markup=kb_atr_bars(lang)
        )

    if 'set_atr_bars+' in type:
        _, period = type.split('+')
        atr_settings = liteDb.getUserAtrSettings(user_id)
        bars = atr_settings[1].split('+')

        liteDb.setUserAtrSettings(
            user_id, (atr_settings[0], f'{period}+{bars[1]}')
        )

        await bot.edit_message_text(
            msg_enter_bars_count(lang), chat_id, mes_id,
            reply_markup=kb_atr_bars_count(lang)
        )
        await bot.set_state(user_id, SettingsState.atr_bars_count, chat_id)

    if 'set_atr_count+' in type:
        _, count = type.split('+')

        atr_settings = liteDb.getUserAtrSettings(user_id)
        bars = atr_settings[1].split('+')
        liteDb.setUserAtrSettings(
            user_id, (atr_settings[0], f'{bars[0]}+{count}'))

        await send_atr_settings(bot, call.message, user_id)

        await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(SettingsCallbackFilter())
    bot.register_callback_query_handler(
        _settings_callback_handler, # type: ignore
        lambda _: True, pass_bot=True,
        settings=settings_factory.filter()
    )
