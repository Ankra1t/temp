from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from config_logger import logger
from models import LANGUAGES, CallbackQuery, User, StateContext
from services import calculation

from service.user_settings_storage import user_settings_storage
from service.advanced_settings_storage import advanced_settings_storage

from states.settings import FirstCalcState, SettingsState

from messages.common import msg_success_edit
from messages.enter import msg_choose_lang, msg_enter_atr_percent, msg_enter_auto_take, msg_enter_bars, msg_enter_bars_count, msg_enter_cancel_at, msg_enter_currency, msg_enter_day_risk, msg_enter_deposit, msg_enter_first_deposit, msg_enter_market, msg_enter_risk_percent, msg_enter_round_count, msg_enter_splitting, msg_enter_summury_profit_type, msg_enter_take_profit, msg_enter_tr_stop, msg_enter_trading_style, msg_enter_trading_type
from messages.settings import msg_choose_exchange_level, msg_confirm_reset, msg_enter_exchange, msg_settings_change_base
from messages.main import msg_success_base_set, msg_welcome

from common.calc_step import choose_calculate_step
from common.utils import edit_message, get_print_float

from keyboards.main import kb_first_calc
from keyboards.settings import (
    kb_settings_auto_take, kb_settings_cancel_at, kb_settings_tr_stop, settings_factory, SettingsCallbackFilter,
    kb_atr_bars, kb_atr_bars_count, kb_change_base, kb_change_currency, kb_change_market, kb_choose_exchange_level,
    kb_choose_lang, kb_base_cancel, kb_enter_exchange, kb_round_count, kb_settings_confirm,
    kb_splitting, kb_splitting_last, kb_stop_type_cancel, kb_trading_style,
    kb_summury_profit_type, kb_take_profit, kb_deposit_cancel, kb_trading_type
)

from pages.calculate import (
    send_active_settings, send_atr_settings, send_calculation, send_confirm_calc_send, send_dop_settings, send_exchange_settings, send_main,
    send_maker_or_taker, send_settings, send_stop_settings, send_summary_profit_settings, send_trading_style_settings,
    send_user_deposit
)
from states.stats import StatsState


async def _settings_callback_handler(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = settings_factory.parse(call.data)
    type = callback_data.get('type', '')

    trading_value = callback_data.get('style', '')
    summury_type = callback_data.get('sum_type', '')
    take_profit_add = callback_data.get('tp', '')
    add_count = callback_data.get('count', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "settings_factory" user_tg_id={user.tgId} type={type} ({trading_value} {summury_type} {take_profit_add} {add_count})')

    if type == 'set_deposit':
        u_base = user_settings_storage.get_or_create(user.tgId)

        current_value = ''
        if u_base is not None and u_base.deposit is not None:
            current_value = f'{get_print_float(u_base.deposit, 2)} {u_base.currency or ""}'

        await bot.edit_message_text(
            msg_enter_deposit(user.lang, current_value),
            chat_id, mes_id,
            reply_markup=kb_deposit_cancel(user.lang)
        )
        await state.set(SettingsState.deposit)

    if type == 'set_risk_percent':
        await bot.edit_message_text(
            msg_enter_risk_percent(user.lang),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user.lang)
        )
        await state.set(SettingsState.risk_percent)

    if type == 'set_day_risk':
        await bot.edit_message_text(
            msg_enter_day_risk(user.lang),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user.lang)
        )
        await state.set(SettingsState.day_risk)

    if type == 'set_round_count':
        if add_count == '':
            u_base = user_settings_storage.get_or_create(user.tgId)

            current_value = -1
            if u_base is not None:
                current_value = u_base.round_count or current_value

            await bot.edit_message_text(
                msg_enter_round_count(user.lang),
                chat_id, mes_id,
                reply_markup=kb_round_count(user.lang, current_value)
            )
            await state.set(SettingsState.round_count)
        else:
            add_count = int(add_count)
            user_settings_storage.set_round_count(
                user.tgId, min(max(add_count, 0), 5))
            await send_user_deposit(bot, call.message, state, user)

    if type == 'trading_style':
        await send_trading_style_settings(bot, call.message, state, user)

    if 'ss_' in type:
        if trading_value == '':
            await state.set(SettingsState.trading_style)
            await bot.edit_message_text(
                msg_enter_trading_style(user.lang),
                chat_id, mes_id,
                reply_markup=kb_trading_style(user.lang)
            )
        else:
            value = trading_value.lower()
            if value == '**off**':
                value = None

            if 'ch_calc' in type:
                async with state.data() as data:
                    stat_id = data.get('stat_id', 0)

                calc_info = calculation.get(userId=user.id, calcId=stat_id)
                if calc_info is None:
                    return

                if value != '**cancel**':
                    # TODO - изменить стиль через api
                    # db.change_calculation_style(stat_id, value)
                    calc_info.tradingStyle = value

                if '+stc' in type:
                    await send_confirm_calc_send(bot, call.message, stat_id)
                else:
                    await send_calculation(
                        bot, call.message,
                        state, user, calc_info
                    )
                await state.delete()

            elif 'calc' in type:
                value = value or False

                await state.add_data(
                    trading_style=value
                )
                await choose_calculate_step(
                    bot, call.message, state, user, True, last_value='trading_style'
                )

            else:
                user_settings_storage.set_trading_style(user.tgId, value)

                if 'welcome' in type:
                    await bot.edit_message_text(
                        msg_success_base_set(user.lang), chat_id, mes_id
                    )
                else:
                    await bot.edit_message_text(
                        msg_success_edit(user.lang), chat_id, mes_id
                    )

                await send_trading_style_settings(bot, call.message, state, user)

    if type == 'switch_style_change':
        user_settings_storage.switch_style_change(user.tgId)
        await send_trading_style_settings(bot, call.message, state, user)

    if 'set_currency' in type:
        if type == 'set_currency':
            await bot.edit_message_text(
                msg_enter_currency(user.lang),
                chat_id, mes_id,
                reply_markup=kb_change_currency(user.lang)
            )
            await state.set(SettingsState.currency)
        else:
            _, currency = type.split('+')

            if 'welcome' in type:
                user_settings_storage.set_currency(user.tgId, currency.upper())
                await state.set(FirstCalcState.deposit)
                await bot.edit_message_text(
                    msg_enter_deposit(user.lang), chat_id, mes_id
                )
            else:
                if 'calc' in type:
                    await state.add_data(
                        currency=currency.upper()
                    )
                    await choose_calculate_step(
                        bot, call.message, state, user, True, last_value='currency'
                    )
                else:
                    user_settings_storage.set_currency(
                        user.tgId, currency.upper())
                    await bot.edit_message_text(
                        msg_success_edit(user.lang), chat_id, mes_id
                    )
                    await send_user_deposit(bot, call.message, state, user, True)

    if 'choose_lang' in type:
        is_edit_lang = False

        for langg in LANGUAGES:
            if f'_{langg}' in type:
                is_edit_lang = True
                user_settings_storage.set_lang(user.tgId, langg)

                if 'first' in type:
                    await bot.edit_message_text(
                        msg_welcome(langg), chat_id, mes_id,
                        reply_markup=kb_first_calc(langg),
                        disable_web_page_preview=True
                    )
                else:
                    await send_settings(bot, call.message, state, user)

        if not is_edit_lang:
            await bot.edit_message_text(
                msg_choose_lang(user.lang),
                chat_id, mes_id,
                reply_markup=kb_choose_lang(user.lang)
            )

    if type == 'go_main':
        await send_main(bot, call.message, state, user)

    if type == 'go_settings':
        await send_settings(bot, call.message, state, user)

    if type == 'go_change_base':
        await bot.edit_message_text(
            msg_settings_change_base(user.lang),
            chat_id, mes_id,
            reply_markup=kb_change_base(user.lang)
        )

    if type == 'first_dep':
        await state.set(FirstCalcState.deposit)
        await bot.edit_message_text(
            msg_enter_first_deposit(user.lang), chat_id, mes_id
        )

    if 'welcome_confirm' in type:
        if 'no' in type:
            await send_main(bot, call.message, state, user, True)
        if 'yes' in type:
            # Переход к логике ввода базовых значений
            await bot.edit_message_text(
                msg_enter_currency(user.lang), chat_id, mes_id,
                reply_markup=kb_change_currency(user.lang, 'welcome')
            )
            await state.set(SettingsState.currency)
            await state.add_data(
                action='welcome'
            )

    if 'reset' in type:
        if '_yes' in type:
            try:
                # Сброс настроек калькулятора до начальных
                user_settings_storage.remove(user.tgId)
                await send_settings(bot, call.message, state, user)
            except:
                # Нет изменений - ничего не изменяется
                pass
        elif '_no' in type:
            await send_settings(bot, call.message, state, user)
        else:
            await bot.edit_message_text(
                msg_confirm_reset(user.lang), chat_id, mes_id,
                reply_markup=kb_settings_confirm(user.lang, 'reset')
            )

    if 'deposit_update' in type:
        if '_on' in type:
            user_settings_storage.set_is_updating_deposit(user.tgId, True)
        elif '_off' in type:
            user_settings_storage.set_is_updating_deposit(user.tgId, False)

        await send_user_deposit(bot, call.message, state, user)

    if type == 'summury_profit':
        # Вывод страницы с "Выводом профита" и его изменением
        await send_summary_profit_settings(bot, call.message, state, user)

    if type == 'change_summury_profit':
        # Если summury_type не задан, то выводим страницу для выбора типа
        # Два типа: с разделением и без
        if summury_type == '':
            await bot.edit_message_text(
                msg_enter_summury_profit_type(user.lang),
                chat_id, mes_id,
                reply_markup=kb_summury_profit_type(user.lang)
            )

            # Стираем state и задаем новый
            # State ничего не отслеживает, задается для сохранения данных
            await state.delete()
            await state.set(SettingsState.summury_profit)
        else:
            # Получаем текущие данные
            async with state.data() as data:
                current_tp_ratio: list[float] = data.get('take_profit', [])
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
            await state.add_data(
                take_profit=current_tp_ratio,
                split=current_split,
            )

            # Далее выводим страницу по summury_type
            if summury_type == 'default':
                await bot.edit_message_text(
                    msg_enter_take_profit(user.lang, current_tp_ratio),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(user.lang, current_tp_ratio)
                )
            elif summury_type == 'splitting':
                if add_count != '':
                    # Если было добавлено больше одного элемента
                    kb = kb_splitting(
                        user.lang, current_tp_ratio, current_split, add_count
                    )
                elif len(current_tp_ratio) == len(current_split):
                    # Если кол-во тейк-профитов и процентов одинаково,
                    # то даем выбрать следующий тейк-профит
                    kb = kb_splitting(
                        user.lang, current_tp_ratio, current_split
                    )
                else:
                    # Иначе даем ввести процент для последнего выбранного тейк-профита
                    kb = None
                    await state.set(SettingsState.splitting)
                await bot.edit_message_text(
                    msg_enter_splitting(
                        user.lang, current_tp_ratio, current_split
                    ),
                    chat_id, mes_id,
                    reply_markup=kb
                )

    if 'save' in type:
        async with state.data() as data:
            current_tp_ratio: list[float] = data.get('take_profit', [])
            current_split: list[float] = data.get('split', [])

        # При сохранении тейк-профита без разделения
        if type == 'tp_save':
            current_tp_ratio.sort()
            user_settings_storage.set_tp_ratio(user.tgId, current_tp_ratio)
            user_settings_storage.set_split_values(user.tgId, None)

        # При сохранении вывода с разделением
        if type == 'splitting_save':
            # Сортируем по возрастанию тейк-профитов
            sorted_tp, sorted_split = zip(
                *sorted(zip(current_tp_ratio, current_split))
            )
            sorted_tp = list(sorted_tp)
            sorted_split = list(sorted_split)

            user_settings_storage.set_tp_ratio(user.tgId, sorted_tp)
            user_settings_storage.set_split_values(user.tgId, sorted_split)

        # Выводим сообщения
        await bot.edit_message_text(msg_success_edit(user.lang), chat_id, mes_id)
        await send_summary_profit_settings(bot, call.message, state, user, True)

    if type == 'splitting_last':
        async with state.data() as data:
            current_tp_ratio: list[float] = data.get('take_profit', [])
            current_split: list[float] = data.get('split', [])

        await bot.edit_message_text(
            msg_enter_splitting(
                user.lang, current_tp_ratio, current_split, True
            ),
            chat_id, mes_id,
            reply_markup=kb_splitting_last(user.lang)
        )

    if 'trading_type' in type:
        if trading_value == '':
            await bot.edit_message_text(
                msg_enter_trading_type(user.lang), chat_id, mes_id,
                reply_markup=kb_trading_type(user.lang)
            )
        else:
            user_settings_storage.set_trading_type(
                user.tgId, trading_value)  # type: ignore
            await send_settings(bot, call.message, state, user)

    if type == 'calc_output':
        # TODO - сейчас только text
        # db.set_user_calc_output(
        #     user.id,
        #     'text'
        # )
        await send_dop_settings(bot, call.message, state, user)

    if type == 'set_first_settings':
        await bot.edit_message_text(
            msg_enter_market(user.lang), chat_id, mes_id,
            reply_markup=kb_change_market(user.lang, 'first')
        )

    if type == 'set_risk_update':
        # TODO - Для чего это было?
        # user_settings_storage.reverseRiskUpdate(user.tgId)
        await send_dop_settings(bot, call.message, state, user)

    if type == 'exchange':
        exchange = user_settings_storage.get_user_exchange(user.tgId)

        if exchange is None:
            await bot.edit_message_text(
                msg_enter_exchange(user.lang),
                chat_id, mes_id,
                reply_markup=kb_enter_exchange(user.lang, is_first=True)
            )
            await state.set(SettingsState.exchange)
            await state.add_data(
                del_mes_id=mes_id
            )
        else:
            await send_exchange_settings(bot, call.message, state, user)

    if 'set_exchange' in type:
        if type == 'set_exchange':
            await bot.edit_message_text(
                msg_enter_exchange(user.lang),
                chat_id, mes_id,
                reply_markup=kb_enter_exchange(user.lang)
            )
            await state.set(SettingsState.exchange)
            await state.add_data(
                del_mes_id=mes_id
            )
        else:
            exchange_value = type.split('++')[1]

            exchange = user_settings_storage.get_exchange_by_name(
                exchange_value)
            if exchange is None:
                return

            if len(exchange.fees) != 0:
                await bot.edit_message_text(
                    msg_choose_exchange_level(user.lang, exchange.fees),
                    chat_id, mes_id,
                    reply_markup=kb_choose_exchange_level(
                        user.lang, exchange.name, [el[0]
                                                   for el in exchange.fees]
                    )
                )
            else:
                await send_maker_or_taker(
                    bot, call.message, state, user,
                    (exchange.name, exchange.maker_fee, exchange.taker_fee)
                )

    if 'set_ex_lvl' in type:
        _, name, lvl_name = type.split('++')

        exchange = user_settings_storage.get_exchange_by_name(name)
        if exchange is None:
            return

        maker_fee, taker_fee = 0, 0
        for fee in exchange.fees:
            if fee[0] == lvl_name:
                maker_fee, taker_fee = fee[1], fee[2]
                break

        await send_maker_or_taker(
            bot, call.message, state, user,
            (exchange.name, maker_fee, taker_fee)
        )

    if type == 'set_fee':
        user_exchange = user_settings_storage.get_user_exchange(user.tgId)

        if user_exchange is None:
            return

        exchange = user_settings_storage.get_exchange_by_name(user_exchange[0])
        if exchange is None:
            return

        if len(exchange.fees) != 0:
            await bot.edit_message_text(
                msg_choose_exchange_level(user.lang, exchange.fees),
                chat_id, mes_id,
                reply_markup=kb_choose_exchange_level(
                    user.lang, exchange.name, [el[0] for el in exchange.fees]
                )
            )
        else:
            await send_maker_or_taker(
                bot, call.message, state, user,
                (exchange.name, exchange.maker_fee, exchange.taker_fee)
            )

        await state.set(SettingsState.fee)
        await state.add_data(
            del_mes_id=mes_id
        )

    if 'set_ex_fee' in type:
        _, name, value = type.split('++')
        user_settings_storage.set_user_exchange(
            user.tgId, (name, float(value)))
        await send_exchange_settings(bot, call.message, state, user)

    if type == 'dop':
        await send_dop_settings(bot, call.message, state, user)

    if 'set_stop' in type:
        _, new_stop_type = type.split('+')

        user_settings_storage.set_is_from_deposit(user.tgId, False)
        if new_stop_type == 'atr_percent':
            await bot.edit_message_text(
                msg_enter_atr_percent(user.lang), chat_id, mes_id,
                reply_markup=kb_stop_type_cancel(user.lang)
            )
            await state.set(SettingsState.atr_percent)
        else:
            user_settings_storage.set_user_stop(user.tgId, new_stop_type)

            if new_stop_type == 'atr':
                await send_atr_settings(bot, call.message, state, user)
            else:
                try:
                    await send_stop_settings(bot, call.message, state, user)
                except:
                    pass

    if type == 'stop_settings':
        await send_stop_settings(bot, call.message, state, user)

    if type == 'change_fr_dp':
        u_base = user_settings_storage.get_or_create(user.tgId)
        curr = False
        if u_base is not None:
            curr = u_base.is_from_deposit

        user_settings_storage.set_is_from_deposit(user.tgId, not curr)
        await send_stop_settings(bot, call.message, state, user)

    if type == 'atr_settings':
        await send_atr_settings(bot, call.message, state, user)

    if type == 'atr_auto':
        atr_settings = user_settings_storage.get_user_atr_settings(user.tgId)
        if atr_settings[0]:
            return

        user_settings_storage.set_user_atr_settings(
            user.tgId, (not atr_settings[0], atr_settings[1])
        )
        await send_atr_settings(bot, call.message, state, user)

    if type == 'atr_self':
        atr_settings = user_settings_storage.get_user_atr_settings(user.tgId)
        if not atr_settings[0]:
            return

        user_settings_storage.set_user_atr_settings(
            user.tgId, (not atr_settings[0], atr_settings[1])
        )
        await send_atr_settings(bot, call.message, state, user)

    if type == 'atr_bars':
        await bot.edit_message_text(
            msg_enter_bars(user.lang), chat_id, mes_id,
            reply_markup=kb_atr_bars(user.lang)
        )

    if 'set_atr_bars+' in type:
        _, period = type.split('+')
        atr_settings = user_settings_storage.get_user_atr_settings(user.tgId)
        bars = atr_settings[1].split('+')

        user_settings_storage.set_user_atr_settings(
            user.tgId, (atr_settings[0], f'{period}+{bars[1]}')
        )

        await bot.edit_message_text(
            msg_enter_bars_count(user.lang), chat_id, mes_id,
            reply_markup=kb_atr_bars_count(user.lang)
        )
        await state.set(SettingsState.atr_bars_count)

    if 'set_atr_count+' in type:
        _, count = type.split('+')

        atr_settings = user_settings_storage.get_user_atr_settings(user.tgId)
        bars = atr_settings[1].split('+')
        user_settings_storage.set_user_atr_settings(
            user.tgId, (atr_settings[0], f'{bars[0]}+{count}'))

        await send_atr_settings(bot, call.message, state, user)

        await bot.answer_callback_query(call.id)

    if type == 'active':
        await send_active_settings(bot, call.message, state, user)

    if type == 'cancel_at':
        await edit_message(
            bot, call.message, 'text',
            msg_enter_cancel_at(user.lang),
            kb_settings_cancel_at(user.lang)
        )
        await state.set(StatsState.cancel_at)
        await state.add_data(
            del_mes_id=mes_id,
            action='settings'
        )

    if 'cancel_at+' in type:
        _, time = type.split('+')

        if time == '0':
            time = None
        elif time == '1h':
            time = 60
        elif time == '4h':
            time = 60 * 4
        else:
            time = 60 * 24

        advanced_settings_storage.update_advanced(user.id, cancelMinutes=time)
        await send_active_settings(bot, call.message, state, user)

    if type == 'tr_stop':
        await edit_message(
            bot, call.message, 'text',
            msg_enter_tr_stop(user.lang),
            kb_settings_tr_stop(user.lang)
        )
        await state.set(StatsState.trailing_stop)
        await state.add_data(
            del_mes_id=mes_id,
            action='settings'
        )

    if 'tr_stop+' in type:
        _, value = type.split('+')

        if value == '0':
            value = None
        else:
            value = float(value)

        advanced_settings_storage.update_advanced(
            user.id,
            trailingStop=value,
            autoTake=None
        )
        await send_active_settings(bot, call.message, state, user)

    if type == 'auto_take':
        await edit_message(
            bot, call.message, 'text',
            msg_enter_auto_take(user.lang),
            kb_settings_auto_take(user.lang)
        )

    if 'auto_take+' in type:
        _, val = type.split('+')

        if val == 'null':
            val = None
        else:
            val = float(val)

        advanced_settings_storage.update_advanced(
            user.id, autoTake=val, trailingStop=None)
        await send_active_settings(bot, call.message, state, user)

    if type == 'auto_stop':
        advSettings = advanced_settings_storage.get_advanced(user.id)
        advanced_settings_storage.update_advanced(
            user.id,
            autoStop=not (advSettings and advSettings.autoStop)
        )
        await send_active_settings(bot, call.message, state, user)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(SettingsCallbackFilter())
    bot.register_callback_query_handler(
        _settings_callback_handler,  # type: ignore
        lambda _: True, pass_bot=True,
        settings=settings_factory.filter()
    )
