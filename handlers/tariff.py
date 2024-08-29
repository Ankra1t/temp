from telebot import TeleBot
from telebot.types import Message

from Classes.YooKassa import yooKassa_create_payment
from config_logger import logger
from db import db
from common.utils import get_lang, text_accept

from states.tariff import TariffState
from keyboards.tariff import kb_bill

from messages.errros import msg_text_error
from messages.users import msg_loading_invoice, msg_bill


def handle_email(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        target_id = data.get('tariff_id', 0)

    email = text_accept(message)
    if email is None:
        bot.send_message(
            chat_id, msg_text_error(lang)
        )
        return

    logger.info(f'callback "handle_email" user_tg_id={user_id} value={email}')

    edit_wait_mess = bot.send_message(
        message.chat.id,
        msg_loading_invoice(user_id)
    )

    tariff = db.get_price_by_id(target_id)
    if tariff is None:
        return

    bot_url = f'https://t.me/{bot.get_me().username}'
    yookassa_payment_url = yooKassa_create_payment(
        user_id, tariff, bot_url, email
    )

    if yookassa_payment_url == False:
        bot.edit_message_text(
            'Ошибка', chat_id, edit_wait_mess.id
        )
        return

    bot.edit_message_text(
        msg_bill(user_id),
        chat_id, edit_wait_mess.id,
        reply_markup=kb_bill(lang, yookassa_payment_url)
    )
    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_email, state=TariffState.email)
