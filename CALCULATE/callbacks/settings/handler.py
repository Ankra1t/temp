import ast
from typing import Any
from telebot import TeleBot
from telebot.types import CallbackQuery
from common.utils import set_state_data

from db_new import db_new, LANGUAGES

from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_choose_lang, msg_enter_currency, msg_enter_deposit,
    msg_enter_risk_percent, msg_enter_split, msg_enter_splitting, msg_enter_summury_profit_type, msg_enter_take_profit, msg_settings_change_base,
    msg_settings_change_market, msg_settings_set_tp_show,
    msg_split_settings, msg_success_edit
)

from .filter import settings_factory, SettingsCallbackFilter
from .keyboards import (
    kb_change_base, kb_change_currency, kb_change_market,
    kb_change_tp_ratio, kb_choose_lang, kb_base_cancel,
    kb_settings, kb_split_ok, kb_split_settings, kb_splitting, kb_summury_profit_type, kb_take_profit
)
from ..pages import send_main, send_settings, send_summury_profit_settings


def _settings_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = settings_factory.parse(call.data)
    type = callback_data.get('type', '')
    summury_type = callback_data.get('summury_type', '')

    temp_str_tp = callback_data.get('take_profit', '')
    current_tp_ratio: list[int] = []
    if temp_str_tp != '':
        try:
            current_tp_ratio = ast.literal_eval(temp_str_tp)
        except:
            current_tp_ratio = []

    temp_str_split = callback_data.get('split', '')
    current_split: list[float] = []
    if temp_str_split != '':
        try:
            current_split = ast.literal_eval(temp_str_split)
        except:
            current_split = []

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

    if 'tp_show' in type:
        tp_ratio = db_new.get_calculator_tp_ratio(user_db_id)
        is_changed = True
        arr_type = type.split('_')

        num, action = arr_type[-2], arr_type[-1]

        if action == 'off':
            if len(tp_ratio) != 1:
                tp_ratio.remove(int(num))
        elif action == 'on':
            tp_ratio.append(int(num))
            tp_ratio.sort()
        else:
            is_changed = False

        if is_changed:
            db_new.set_user_is_splitting(user_db_id, False)

        if is_changed or len(arr_type) == 2:
            db_new.set_calculator_tp_ratio(user_db_id, tp_ratio)
            bot.edit_message_text(
                msg_settings_set_tp_show(user_id), chat_id, mes_id,
                reply_markup=kb_change_tp_ratio(user_id, tp_ratio)
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

    if type == 'split':
        bot.edit_message_text(
            msg_split_settings(user_id), chat_id, mes_id,
            reply_markup=kb_split_settings(user_id)
        )

    if type == 'split_on' or type == 'split_off':
        is_splitting = True if type == 'split_on' else False

        if is_splitting:
            split_values = db_new.get_user_split_values(user_db_id)
            tp_ratio = db_new.get_calculator_tp_ratio(user_db_id)

            if len(split_values) != len(tp_ratio):
                bot.edit_message_text(
                    'Для включения "разделения" нужно установить значения',
                    chat_id, mes_id, reply_markup=kb_split_ok(user_id)
                )
                return

        db_new.set_user_is_splitting(user_db_id, is_splitting)

        bot.edit_message_text(
            msg_split_settings(user_id), chat_id, mes_id,
            reply_markup=kb_split_settings(user_id)
        )

    if type == 'split_set_value':
        bot.edit_message_text(
            msg_enter_split(user_id),
            chat_id, mes_id
        )
        bot.set_state(user_id, SettingsState.split_values, chat_id)

    if type == 'summury_profit':
        send_summury_profit_settings(bot, call.message, user_id)

    if type == 'change_summury_profit':
        if summury_type == '':
            bot.edit_message_text(
                msg_enter_summury_profit_type(user_id),
                chat_id, mes_id,
                reply_markup=kb_summury_profit_type(user_id)
            )
        elif summury_type == 'default':
            bot.edit_message_text(
                msg_enter_take_profit(user_id, current_tp_ratio),
                chat_id, mes_id,
                reply_markup=kb_take_profit(user_id, current_tp_ratio)
            )
        elif summury_type == 'splitting':
            if len(current_tp_ratio) == len(current_split):
                bot.edit_message_text(
                    msg_enter_splitting(
                        user_id, current_tp_ratio, current_split),
                    chat_id, mes_id,
                    reply_markup=kb_splitting(
                        user_id, current_tp_ratio, current_split
                    )
                )
            else:
                bot.set_state(user_id, '', chat_id)
                set_state_data(bot, user_id, chat_id, {
                    'take_profit': current_tp_ratio,
                    'split': current_split
                })
                bot.edit_message_text(
                    msg_enter_splitting(
                        user_id, current_tp_ratio, current_split
                    ),
                    chat_id, mes_id,
                    reply_markup=kb_splitting(
                        user_id, current_tp_ratio, current_split, True
                    )
                )

    if type == 'tp_save':
        current_tp_ratio.sort()
        db_new.set_calculator_tp_ratio(user_db_id, current_tp_ratio)
        db_new.set_user_is_splitting(user_db_id, False)

    if type == 'splitting_save':
        current_tp_ratio.sort()
        current_split.sort()

        db_new.set_calculator_tp_ratio(user_db_id, current_tp_ratio)
        db_new.set_user_is_splitting(user_db_id, True)
        db_new.set_user_split_values(user_db_id, current_split)

    if 'save' in type:
        bot.edit_message_text('Изменено!', chat_id, mes_id)
        send_summury_profit_settings(bot, call.message, user_id, True)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(SettingsCallbackFilter())
    bot.register_callback_query_handler(
        _settings_callback_handler,
        lambda _: True, pass_bot=True,
        settings=settings_factory.filter())
