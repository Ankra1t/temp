from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage
from telebot.states.asyncio.context import StateContext

from config_logger import logger
from Classes.CryptoBot import cryptoPay_create_payment
from common.utils import delete_message, get_lang
from models import CallbackQuery
from db import db

from states.tariff import TariffState
from messages.users import msg_is_subscribed, msg_loading_invoice, msg_bill

from keyboards.tariff import (
    user_tariff_factory, UserTariffCallbackFilter,
    kb_bill, kb_user_tariff_back
)

from pages.calculate import send_main, send_tariffs_list_item


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data: dict = user_tariff_factory.parse(call.data)
    type = callback_data.get('type', '')
    target_id = callback_data.get('tariff_id', '')
    tariff_type = callback_data.get('tariff_type', '')
    page = int(callback_data.get('page', 0))

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    lang = get_lang(user_id)

    is_rus = call.from_user.language_code == 'ru'

    logger.info(
        f'callback "user_main_factory" user_tg_id={user_id} type={type} ({target_id} {tariff_type} {page})')

    if type == 'go_main':
        await send_main(call.message, bot, user_id)

    elif 'go_tariff' in type:
        await send_tariffs_list_item(
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
        state.set(TariffState.email)
        state.add_data(tariff_id=target_id)

    elif type == 'pay_tariff_cb':
        if is_rus:
            return

        await delete_message(bot, chat_id, mes_id)
        user_db_id = db.get_user_id_by_tg_id(user_id)
        user_sub = db.get_current_subscribe_user(user_db_id)

        if user_sub is not None:
            await bot.send_message(
                chat_id, msg_is_subscribed(user_id),
                reply_markup=kb_user_tariff_back(lang)
            )
            return

        edit_wait_mess = await bot.send_message(
            call.message.chat.id,
            msg_loading_invoice(user_id)
        )

        tariff = db.get_price_by_id(target_id)
        if tariff is None:
            return

        bot_url = f'https://t.me/{(await bot.get_me()).username}'
        cryptopay_payment_url = cryptoPay_create_payment(
            user_id, tariff, bot_url
        )

        if cryptopay_payment_url == False:
            await bot.edit_message_text(
                'Ошибка', chat_id, edit_wait_mess.id
            )
            return

        await bot.edit_message_text(
            msg_bill(user_id),
            chat_id, edit_wait_mess.id,
            reply_markup=kb_bill(lang, cryptopay_payment_url)
        )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(UserTariffCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore
        lambda _: True, pass_bot=True,
        user_tariff=user_tariff_factory.filter()
    )
