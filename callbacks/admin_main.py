import os
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage, InputFile

from common.utils import delete_message
from models import CallbackQuery, StateContext, User

from keyboards.admin_main import admin_main_factory, AdminMainCallbackFilter, kb_tools_list_back

from pages.calculate import send_admin_send_settings
from pages.user import send_site_code
from pages.admin import (
    send_admin_main, send_admin_tools_list, send_admin_users, send_admin_fut_posts, send_admin_workers,
    send_admin_params, send_admin_payment, send_admin_tariffs
)
from services import ticker
from states.admin_params import AdminMainState


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_main_factory.parse(call.data)
    type = callback_data.get('type', '')
    value = callback_data.get('value', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'users':
        await send_admin_users(bot, call.message, state)

    if type == 'workers':
        await send_admin_workers(bot, call.message, state)

    if type == 'fut_posts':
        await send_admin_fut_posts(bot, call.message, state)

    if type == 'tariffs':
        await send_admin_tariffs(bot, call.message, state)

    if type == 'params':
        await send_admin_params(bot, call.message, state)

    if type == 'payment':
        await send_admin_payment(bot, call.message, state)

    if type == 'site_code':
        await send_site_code(bot, call.message, state, user)

    if type == 'back':
        await send_admin_main(bot, call.message, state)

    if type == 'send_settings':
        await send_admin_send_settings(bot, call.message, state, user)

    if type == 'tools':
        await send_admin_tools_list(bot, call.message, value)

    if type == 'tools_spot' or type == 'tools_default':
        isSpot = type == 'tools_spot'

        await delete_message(
            bot, chat_id, mes_id
        )

        text = ticker.get_text(
            isSpot,
            (float(value) * (10 ** 6)) if value != '' else None
        ) or ''

        filename = f'ByBit{chat_id}.txt'
        text_file = open(filename, 'w+')
        text_file.write(text)
        text_file.close()

        await bot.send_document(
            chat_id, InputFile(
                filename, 'ByBit.txt'
            )
        )

        os.remove(filename)

        await send_admin_tools_list(bot, call.message, value, True)

    if type == 'tools_turnover':
        current = ''
        if value:
            current = f'Сейчас от: {value}M USDT\n'
        await bot.edit_message_text(
            f'{current}Введите оборот в миллионах:',
            chat_id, mes_id,
            reply_markup=kb_tools_list_back(value)
        )
        await state.set(AdminMainState.turnover)
        await state.add_data(del_mes_id=mes_id)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore # TODO - check
        lambda _: True, pass_bot=True,
        admin_main=admin_main_factory.filter()
    )
