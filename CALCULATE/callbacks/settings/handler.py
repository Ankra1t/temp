from typing import Any
from telebot import TeleBot
from telebot.types import CallbackQuery
from CALCULATE.callbacks.utils import choose_calculate_step

from db import db, LANGUAGES

from common.utils import set_state_data
from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_choose_lang, msg_confirm_reset, msg_enter_currency, msg_enter_day_risk, msg_enter_deposit,
    msg_enter_risk_percent, msg_enter_round_count, msg_enter_splitting,
    msg_enter_summury_profit_type, msg_enter_take_profit, msg_enter_trading_style,
    msg_settings_change_market, msg_success_base_set, msg_success_edit, msg_settings_change_base,
)

from .filter import settings_factory, SettingsCallbackFilter
from .keyboards import (
    kb_change_base, kb_change_currency, kb_change_market,
    kb_choose_lang, kb_base_cancel, kb_settings_confirm,
    kb_splitting, kb_splitting_last, kb_trading_style,
    kb_summury_profit_type, kb_take_profit
)
from ..pages import send_main, send_settings, send_summury_profit_settings


def _settings_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = settings_factory.parse(call.data)
    type = callback_data.get('type', '')

    trading_style = callback_data.get('trading_style', '')
    summury_type = callback_data.get('summury_type', '')
    take_profit_add = callback_data.get('take_profit', '')
    add_count = callback_data.get('add_count', '')

    user_id = call.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'set_deposit':
        bot.edit_message_text(
            msg_enter_deposit(user_id),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user_id)
        )
        bot.set_state(user_id, SettingsState.deposit, chat_id)

    if type == 'set_risk_percent':
        bot.edit_message_text(
            msg_enter_risk_percent(user_id),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user_id)
        )
        bot.set_state(user_id, SettingsState.risk_percent, chat_id)

    if type == 'set_day_risk':
        bot.edit_message_text(
            msg_enter_day_risk(user_id),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user_id)
        )
        bot.set_state(user_id, SettingsState.day_risk, chat_id)

    if type == 'set_round_count':
        bot.edit_message_text(
            msg_enter_round_count(user_id),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user_id)
        )
        bot.set_state(user_id, SettingsState.round_count, chat_id)

    if 'style' in type:
        if trading_style == '':
            bot.set_state(user_id, SettingsState.trading_style, chat_id)
            bot.edit_message_text(
                msg_enter_trading_style(user_id),
                chat_id, mes_id,
                reply_markup=kb_trading_style(user_id)
            )
        else:
            value = trading_style.lower()
            if value == '**off**':
                value = None

            db.set_user_trading_style(user_db_id, value)

            if 'calc' in type:
                value = value or False

                set_state_data(
                    bot, user_id, chat_id, {
                        'trading_style': value
                    }
                )
                choose_calculate_step(bot, user_id, chat_id, mes_id, True)
            else:
                if 'welcome' in type:
                    bot.edit_message_text(
                        msg_success_base_set(user_id), chat_id, mes_id
                    )
                else:
                    bot.edit_message_text(
                        msg_success_edit(user_id), chat_id, mes_id
                    )

                send_settings(bot, call.message, user_id, True)

    if 'set_currency' in type:
        if type == 'set_currency':
            bot.edit_message_text(
                msg_enter_currency(user_id),
                chat_id, mes_id,
                reply_markup=kb_change_currency(user_id)
            )
            bot.set_state(user_id, SettingsState.currency, chat_id)
        else:
            _, currency = type.split('+')
            db.set_user_currency(user_db_id, currency.upper())

            if 'welcome' in type:
                bot.set_state(user_id, SettingsState.deposit, chat_id)
                bot.edit_message_text(
                    msg_enter_deposit(user_id), chat_id, mes_id
                )
            else:
                if 'calc' in type:
                    choose_calculate_step(bot, user_id, chat_id, mes_id, True)
                else:
                    bot.edit_message_text(
                        msg_success_edit(user_id), chat_id, mes_id
                    )
                    send_settings(bot, call.message, user_id, True)

    if 'choose_lang' in type:
        is_edit_lang = False

        for lang in LANGUAGES:
            if f'_{lang}' in type:
                is_edit_lang = True
                db.set_user_lang(user_db_id, lang)
                send_settings(bot, call.message, user_id)

        if not is_edit_lang:
            bot.edit_message_text(
                msg_choose_lang(user_id),
                chat_id, mes_id,
                reply_markup=kb_choose_lang(user_id)
            )

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if type == 'go_settings':
        send_settings(bot, call.message, user_id)

    if type == 'go_change_base':
        bot.edit_message_text(
            msg_settings_change_base(user_id),
            chat_id, mes_id,
            reply_markup=kb_change_base(user_id)
        )

    if 'market' in type:
        type_list = type.split('_')

        if len(type_list) == 1:
            bot.edit_message_text(
                msg_settings_change_market(user_id),
                chat_id, mes_id,
                reply_markup=kb_change_market(user_id)
            )
        else:
            market: Any = type_list[1]
            db.set_calculator_user_market(user_db_id, market)
            send_settings(bot, call.message, user_id)

    if 'welcome_confirm' in type:
        if 'no' in type:
            send_main(call.message, bot, user_id, True)
        if 'yes' in type:
            # Переход к логике ввода базовых значений
            bot.edit_message_text(
                msg_enter_currency(user_id), chat_id, mes_id,
                reply_markup=kb_change_currency(user_id, 'welcome')
            )
            bot.set_state(user_id, SettingsState.currency, chat_id)
            set_state_data(bot, user_id, chat_id, {'action': 'welcome'})

    if 'reset' in type:
        if '_yes' in type:
            try:
                # Сброс настроек калькулятора до начальных
                db.reset_user_settings(user_db_id)
                send_settings(bot, call.message, user_id)
            except:
                # Нет изменений - ничего не изменяется
                pass
        elif '_no' in type:
            send_settings(bot, call.message, user_id)
        else:
            bot.edit_message_text(
                msg_confirm_reset(user_id), chat_id, mes_id,
                reply_markup=kb_settings_confirm(user_id, 'reset')
            )

    if type == 'summury_profit':
        # Вывод страницы с "Выводом профита" и его изменением
        send_summury_profit_settings(bot, call.message, user_id)

    if type == 'change_summury_profit':
        # Если summury_type не задан, то выводим страницу для выбора типа
        # Два типа: с разделением и без
        if summury_type == '':
            bot.edit_message_text(
                msg_enter_summury_profit_type(user_id),
                chat_id, mes_id,
                reply_markup=kb_summury_profit_type(user_id)
            )

            # Стираем state и задаем новый
            # State ничего не отслеживает, задается для сохранения данных
            bot.delete_state(user_id, chat_id)
            bot.set_state(user_id, SettingsState.summury_profit, chat_id)
        else:
            with bot.retrieve_data(user_id, chat_id) as data:
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
                bot.edit_message_text(
                    msg_enter_take_profit(user_id, current_tp_ratio),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(user_id, current_tp_ratio)
                )
            elif summury_type == 'splitting':
                if add_count != '':
                    # Если было добавлено больше одного элемента
                    kb = kb_splitting(
                        user_id, current_tp_ratio, current_split, add_count
                    )
                elif len(current_tp_ratio) == len(current_split):
                    # Если кол-во тейк-профитов и процентов одинаково,
                    # то даем выбрать следующий тейк-профит
                    kb = kb_splitting(
                        user_id, current_tp_ratio, current_split
                    )
                else:
                    # Иначе даем ввести процент для последнего выбранного тейк-профита
                    kb = None
                    bot.set_state(user_id, SettingsState.splitting, chat_id)
                bot.edit_message_text(
                    msg_enter_splitting(
                        user_id, current_tp_ratio, current_split
                    ),
                    chat_id, mes_id,
                    reply_markup=kb
                )

    if 'save' in type:
        with bot.retrieve_data(user_id, chat_id) as data:
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
        bot.edit_message_text('Изменено!', chat_id, mes_id)
        send_summury_profit_settings(bot, call.message, user_id, True)

    if type == 'splitting_last':
        with bot.retrieve_data(user_id, chat_id) as data:
            current_tp_ratio: list[int] = data.get('take_profit', [])
            current_split: list[float] = data.get('split', [])

        bot.edit_message_text(
            msg_enter_splitting(
                user_id, current_tp_ratio, current_split, True
            ),
            chat_id, mes_id,
            reply_markup=kb_splitting_last(user_id)
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(SettingsCallbackFilter())
    bot.register_callback_query_handler(
        _settings_callback_handler,
        lambda _: True, pass_bot=True,
        settings=settings_factory.filter())
