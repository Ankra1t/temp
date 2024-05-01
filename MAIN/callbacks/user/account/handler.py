from telebot import TeleBot
from telebot.types import CallbackQuery

from config_logger import logger
from db import db

from .keyboards import kb_user_purchases, kb_user_referral, kb_user_referral_list
from .filter import user_account_factory, UserAccountCallbackFilter

from MAIN.states import UserAccountState
from MAIN.callbacks import send_user_account, send_user_main
from MAIN.common.messages import msg_referral, msg_referral_list, msg_user_purchases


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_account_factory.parse(call.data)
    type = callback_data.get('type') or ''

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    logger.info(f'callback "user_account_factory" user_tg_id={user_id} type={type}')

    if type == 'purchases':
        purchases = db.get_purchases_by_user(user_id)

        bot.edit_message_text(
            msg_user_purchases(user_id, purchases),
            chat_id, mes_id,
            reply_markup=kb_user_purchases(user_id)
        )

    if type == 'main':
        send_user_main(bot, call.message, user_id)

    if type == 'back':
        send_user_account(bot, call.message, user_id)

    if type == 'referral':
        user_db_id = db.get_user_id_by_tg_id(user_id)
        referals_count = len(db.get_user_referals(user_db_id))

        text = msg_referral(user_id, referals_count, bot.get_me().username)

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_user_referral(user_id, referals_count)
        )

    if type == 'referral_list':
        user_db_id = db.get_user_id_by_tg_id(user_id)
        referrals = db.get_user_referals(user_db_id)

        text = msg_referral_list(user_id, referrals)

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_user_referral_list(user_id)
        )

    if type == 'password':
        bot.edit_message_text(
            'Введите новый пароль:', chat_id, mes_id
        )
        bot.set_state(user_id, UserAccountState.password, chat_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserAccountCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_account=user_account_factory.filter())
