from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import MANUAL_TYPE, CallbackQuery, StateContext, User
from messages.common import msg_manuals

from keyboards.manual import manual_factory, ManualCallbackFilter
from pages.calculate import send_main, send_manual


async def _manual_callback_handler(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data: dict = manual_factory.parse(call.data)
    type = callback_data['type']
    page = int(callback_data['page'])

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'main':
        await send_main(bot, call.message, state, user)

    if 'manual' in type:
        type_arr = type.split('+')
        manual_type: MANUAL_TYPE = 'calc'
        if len(type_arr) == 2:
            manual_type = type_arr[1]  # type: ignore

        await send_manual(bot, call.message, state, user, manual_type)

    if type == 'prev':
        page -= 1
    elif type == 'next':
        page += 1
    elif type == 'start':
        page = 1
    elif type == 'end':
        page = len(msg_manuals)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(ManualCallbackFilter())
    bot.register_callback_query_handler(
        _manual_callback_handler, # type: ignore
        lambda _: True, pass_bot=True,
        manual=manual_factory.filter())
