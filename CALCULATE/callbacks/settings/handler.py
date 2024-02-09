from typing import Any
from telebot import TeleBot
from telebot.types import CallbackQuery
from common.utils import set_state_data

from db_new import db_new, LANGUAGES

from CALCULATE.states import SettingsState
from CALCULATE.common.messages import (
    msg_choose_lang, msg_enter_currency, msg_enter_deposit,
    msg_enter_risk_percent, msg_settings_change_base, msg_settings_change_market, msg_settings_set_tp_show, msg_success_edit
)

from .filter import settings_factory, SettingsCallbackFilter
from .keyboards import kb_change_base, kb_change_currency, kb_change_market, kb_change_tp_show, kb_choose_lang, kb_base_cancel, kb_settings
from ..pages import send_main, send_settings


def _settings_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = settings_factory.parse(call.data)
    type = callback_data.get('type', '')

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
        tp_show = db_new.get_calculator_tp_show(user_db_id) or '345'
        is_changed = True
        arr_type = type.split('_')

        num, action = arr_type[-2], arr_type[-1]

        if action == 'off':
            if len(tp_show) != 1:
                tp_show = tp_show.replace(num, '')
        elif action == 'on':
            tp_show = list(map(lambda x: int(x), tp_show))
            tp_show.append(int(num))
            tp_show.sort()
            tp_show = ''.join(list(map(lambda x: str(x), tp_show)))
        else:
            is_changed = False

        if is_changed or len(arr_type) == 2:
            db_new.set_calculator_tp_show(user_db_id, tp_show)
            bot.edit_message_text(
                msg_settings_set_tp_show(user_id), chat_id, mes_id,
                reply_markup=kb_change_tp_show(user_id, tp_show)
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

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(SettingsCallbackFilter())
    bot.register_callback_query_handler(
        _settings_callback_handler,
        lambda _: True, pass_bot=True,
        settings=settings_factory.filter())
