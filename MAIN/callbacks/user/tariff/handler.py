from telebot import TeleBot
from telebot.types import CallbackQuery

from Classes.YooKassa import create_payment
from MAIN.callbacks.user.pages import send_tariffs_list_item
from common.utils import check_discount_price
from db import db
from messages.users import msg_is_subscribed, msg_loading_invoice, msg_yookassa

from MAIN.callbacks import send_user_tariffs, send_user_main

from .filter import user_tariff_factory, UserTariffCallbackFilter
from .keyboards import kb_bill_yookassa, kb_user_tariff_back


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_tariff_factory.parse(call.data)
    type = callback_data.get('type', '')
    target_id = callback_data.get('tariff_id', '')
    tariff_type = callback_data.get('tariff_type', '')
    page = int(callback_data.get('page', 0))

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'go_main':
        send_user_main(bot, call.message, user_id)

    if 'go_tariff' in type:
        del_mes = 'del' in type

        send_user_tariffs(bot, call.message, user_id, del_mes)

        if del_mes:
            bot.delete_message(chat_id, mes_id)

    if type == 'pay_tariff':
        bot.delete_message(chat_id, mes_id)

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
        price = check_discount_price(tariff)
        payment_url = create_payment(
            user_id, tariff, bot_url
        )

        if payment_url == False:
            bot.edit_message_text(
                'Ошибка', chat_id, edit_wait_mess.id
            )
            return

        bot.edit_message_text(
            msg_yookassa(user_id),
            chat_id, edit_wait_mess.id,
            reply_markup=kb_bill_yookassa(
                user_id, f'{price} {tariff.currency}', payment_url
            )
        )

    if type == 'get_tariff':
        send_tariffs_list_item(
            bot, call.message, user_id, tariff_type, page
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserTariffCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_tariff=user_tariff_factory.filter()
    )
