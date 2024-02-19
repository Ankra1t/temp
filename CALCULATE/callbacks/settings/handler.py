from typing import Any
from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new, LANGUAGES

from common.utils import set_state_data
from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_choose_lang, msg_enter_currency, msg_enter_deposit,
    msg_enter_risk_percent, msg_enter_splitting,
    msg_enter_summury_profit_type, msg_enter_take_profit,
    msg_settings_change_market, msg_success_edit, msg_settings_change_base,
)

from .filter import settings_factory, SettingsCallbackFilter
from .keyboards import (
    kb_change_base, kb_change_currency, kb_change_market,
    kb_choose_lang, kb_base_cancel,
    kb_splitting, kb_splitting_last,
    kb_summury_profit_type, kb_take_profit
)
from ..pages import send_main, send_settings, send_summury_profit_settings


def _settings_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = settings_factory.parse(call.data)
    type = callback_data.get('type', '')

    summury_type = callback_data.get('summury_type', '')
    take_profit_add = callback_data.get('take_profit', '')
    add_count = callback_data.get('add_count', '')

    user_id = call.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'set_deposit':
        bot.edit_message_text(
            msg_enter_deposit(user_id),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user_id))
        bot.set_state(user_id, SettingsState.deposit, chat_id)

    if type == 'set_risk_percent':
        bot.edit_message_text(
            msg_enter_risk_percent(user_id),
            chat_id, mes_id,
            reply_markup=kb_base_cancel(user_id)
        )
        bot.set_state(user_id, SettingsState.risk_percent, chat_id)

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

            db_new.set_user_currency(user_db_id, currency)

            bot.edit_message_text(msg_success_edit(user_id), chat_id, mes_id)
            send_settings(bot, call.message, user_id, True)

    if 'choose_lang' in type:
        is_edit_lang = False

        for lang in LANGUAGES:
            if f'_{lang}' in type:
                is_edit_lang = True
                db_new.set_user_lang(user_db_id, lang)
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

            db_new.set_calculator_user_market(user_db_id, market)

            send_settings(bot, call.message, user_id)

    if 'welcome_confirm' in type:
        if 'no' in type:
            send_main(call.message, bot, user_id, True)
        if 'yes' in type:
            bot.edit_message_text(
                msg_enter_deposit(user_id), chat_id, mes_id
            )
            bot.set_state(user_id, SettingsState.deposit, chat_id)
            set_state_data(bot, user_id, chat_id, {'action': 'welcome'})

    if type == 'reset':
        db_new.reset_user_settings(user_db_id)
        send_settings(bot, call.message, user_id)

    if type == 'summury_profit':
        send_summury_profit_settings(bot, call.message, user_id)

    if type == 'change_summury_profit':
        if summury_type == '':
            bot.edit_message_text(
                msg_enter_summury_profit_type(user_id),
                chat_id, mes_id,
                reply_markup=kb_summury_profit_type(user_id)
            )
            bot.delete_state(user_id, chat_id)
            bot.set_state(user_id, SettingsState.summury_profit, chat_id)
        else:
            with bot.retrieve_data(user_id, chat_id) as data:
                current_tp_ratio: list[int] = data.get('take_profit', [])
                current_split: list[float] = data.get('split', [])

                if add_count != '':
                    add_count = int(add_count)

                    if add_count < 0:
                        current_tp_ratio = current_tp_ratio[:add_count]
                        current_split = current_split[:add_count]
                    else:
                        max_tp = max(current_tp_ratio)

                        percents_sum = sum(current_split)
                        if abs(percents_sum - 100) < 0.1:
                            percents_sum = 100
                        new_percent = round(
                            (100 - percents_sum) / add_count, 2
                        )

                        for i in range(1, add_count + 1):
                            current_tp_ratio.append(max_tp + i)
                            current_split.append(new_percent)

                if take_profit_add != '':
                    take_profit_add = int(take_profit_add)
                    current_tp_ratio.append(int(take_profit_add))

                data['take_profit'] = current_tp_ratio
                data['split'] = current_split

            if summury_type == 'default':
                bot.edit_message_text(
                    msg_enter_take_profit(user_id, current_tp_ratio),
                    chat_id, mes_id,
                    reply_markup=kb_take_profit(user_id, current_tp_ratio)
                )
            elif summury_type == 'splitting':
                if add_count != '':
                    kb = kb_splitting(
                        user_id, current_tp_ratio, current_split,
                        False, add_count
                    )
                elif len(current_tp_ratio) == len(current_split):
                    kb = kb_splitting(
                        user_id, current_tp_ratio, current_split
                    )
                else:
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

        if type == 'tp_save':
            current_tp_ratio.sort()
            db_new.set_calculator_tp_ratio(user_db_id, current_tp_ratio)
            db_new.set_user_is_splitting(user_db_id, False)

        if type == 'splitting_save':
            sorted_tp, sorted_split = zip(
                *sorted(zip(current_tp_ratio, current_split))
            )
            sorted_tp = list(sorted_tp)
            sorted_split = list(sorted_split)

            db_new.set_calculator_tp_ratio(user_db_id, sorted_tp)
            db_new.set_user_split_values(user_db_id, sorted_split)
            db_new.set_user_is_splitting(user_db_id, True)

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
