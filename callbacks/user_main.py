from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from config_logger import logger
from models import CallbackQuery, StateContext, User

from common.calc_step import send_calc_start
from common.utils import send_in_development

from keyboards.user_main import user_main_factory, UserMainCallbackFilter

from pages.calculate import send_main
from pages.admin import send_admin_main
from pages.user import send_user_education, send_user_account, send_user_main


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data: dict = user_main_factory.parse(call.data)
    type = callback_data.get('type', '')

    user_id = call.from_user.id

    logger.info(
        f'callback "user_main_factory" user_tg_id={user_id} type={type}')

    role = 0

    if type == 'main':
        if role == 1:
            await send_admin_main(bot, call.message, state)
        else:
            await send_user_main(bot, call.message, state, user)

    if type == 'education':
        await send_user_education(bot, call.message, state)

    if type == 'account':
        await send_user_account(bot, call.message, state, user)

    if type == 'calculator':
        await send_main(bot, call.message, state, user)

    if type == 'try':
        await send_calc_start(bot, call.message, state, user, is_try=True)

    if type == 'signals':
        await send_in_development(bot, call.message)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(UserMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        user_main=user_main_factory.filter()
    )
