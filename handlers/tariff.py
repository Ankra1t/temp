from telebot.async_telebot import AsyncTeleBot

from Classes.YooKassa import yooKassa_create_payment
from config_logger import logger
from db import db
from models import Message, StateContext, User
from common.utils import text_accept

from states.tariff import TariffState
from keyboards.tariff import kb_bill

from messages.errros import msg_text_error
from messages.users import msg_loading_invoice, msg_bill


async def handle_email(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    async with state.data() as data:
        target_id = data.get('tariff_id', 0)

    email = text_accept(message)
    if email is None:
        await bot.send_message(
            chat_id, msg_text_error(user.lang)
        )
        return

    logger.info(f'callback "handle_email" user_tg_id={user.tgId} value={email}')

    edit_wait_mess = await bot.send_message(
        message.chat.id,
        msg_loading_invoice(user.lang)
    )

    tariff = db.get_price_by_id(target_id)
    if tariff is None:
        return

    bot_url = f'https://t.me/{(await bot.get_me()).username}'
    yookassa_payment_url = yooKassa_create_payment(
        user.tgId, tariff, bot_url, email
    )

    if yookassa_payment_url == False:
        await bot.edit_message_text(
            'Ошибка', chat_id, edit_wait_mess.id
        )
        return

    await bot.edit_message_text(
        msg_bill(user.lang),
        chat_id, edit_wait_mess.id,
        reply_markup=kb_bill(user.lang, yookassa_payment_url)
    )
    await state.delete()


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_email, state=TariffState.email)
