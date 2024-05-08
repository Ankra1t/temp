from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.common.messages import msg_enter_email
from CALCULATE.states.tariff import TariffState
from config_logger import logger
from Classes.CryptoBot import cryptoPay_create_payment
from common.utils import delete_message, set_state_data
from db import db
from messages.users import msg_is_subscribed, msg_loading_invoice, msg_bill

from .filter import user_tariff_factory, UserTariffCallbackFilter
from .keyboards import kb_bill, kb_user_tariff_back
from ..pages import send_main, send_tariffs_list_item


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_tariff_factory.parse(call.data)
    type = callback_data.get('type', '')
    target_id = callback_data.get('tariff_id', '')
    tariff_type = callback_data.get('tariff_type', '')
    page = int(callback_data.get('page', 0))

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    is_rus = call.from_user.language_code == 'ru'

    logger.info(
        f'callback "user_main_factory" user_tg_id={user_id} type={type} ({target_id} {tariff_type} {page})')

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    elif 'go_tariff' in type:
        send_tariffs_list_item(
            bot, call.message, user_id, 'calc', page, is_rus
        )

    elif type == 'pay_tariff_yoo':
        return
        delete_message(bot, chat_id, mes_id)

        user_db_id = db.get_user_id_by_tg_id(user_id)
        user_sub = db.get_current_subscribe_user(user_db_id)

        if user_sub is not None:
            bot.send_message(
                chat_id, msg_is_subscribed(user_id),
                reply_markup=kb_user_tariff_back(user_id)
            )
            return

        bot.send_message(chat_id, msg_enter_email(user_id))
        bot.set_state(user_id, TariffState.email, chat_id)
        set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})

    elif type == 'pay_tariff_cb':
        if is_rus:
            return

        delete_message(bot, chat_id, mes_id)
        user_db_id = db.get_user_id_by_tg_id(user_id)
        user_sub = db.get_current_subscribe_user(user_db_id)

        if user_sub is not None:
            bot.send_message(
                chat_id, msg_is_subscribed(user_id),
                reply_markup=kb_user_tariff_back(user_id)
            )
            return

        edit_wait_mess = bot.send_message(
            call.message.chat.id,
            msg_loading_invoice(user_id)
        )

        tariff = db.get_price_by_id(target_id)
        if tariff is None:
            return

        bot_url = f'https://t.me/{bot.get_me().username}'
        cryptopay_payment_url = cryptoPay_create_payment(
            user_id, tariff, bot_url
        )

        if cryptopay_payment_url == False:
            bot.edit_message_text(
                'Ошибка', chat_id, edit_wait_mess.id
            )
            return

        bot.edit_message_text(
            msg_bill(user_id),
            chat_id, edit_wait_mess.id,
            reply_markup=kb_bill(user_id, cryptopay_payment_url)
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserTariffCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_tariff=user_tariff_factory.filter()
    )
