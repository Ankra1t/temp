from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from config_logger import logger
from messages.enter import msg_choose_lang
from messages.main import msg_support
from models import LANGUAGES, CallbackQuery, StateContext, User

from messages.profile import msg_enter_nickname

from service.user_settings_storage import user_settings_storage
from states.account import UserAccountState
from keyboards.account import (
    user_account_factory, UserAccountCallbackFilter,
    kb_params_choose_lang, kb_support, kb_user_params_back,
)

from pages.user import send_referral, send_user_account, send_user_main, send_user_params


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = user_account_factory.parse(call.data)
    type = callback_data.get('type') or ''

    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(
        f'callback "user_account_factory" user_tg_id={user.tgId} type={type}'
    )

    if type == 'main':
        await send_user_main(bot, call.message, state, user)

    if type == 'back':
        await send_user_account(bot, call.message, state, user)

    if type == 'support':
        sup = 'calcsup'  # TODO: получать из API
        msg = msg_support(user.lang)

        await bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=kb_support(user.lang, sup)
        )
        await state.delete()

    if type == 'referral':
        await send_referral(bot, call.message, state, user)

    if type == 'referral_list':
        # TODO: Получить список рефералов через API
        await bot.edit_message_text(
            'Функция в разработке',
            chat_id, mes_id
        )

    if type == 'params':
        await send_user_params(bot, call.message, state, user)

    if 'set_lang' in type:
        is_edit_lang = False

        for lang in LANGUAGES:
            if f'_{lang}' in type:
                is_edit_lang = True
                user_settings_storage.set_lang(user.tgId, lang)
                await send_user_params(bot, call.message, state, user)

        if not is_edit_lang:
            await bot.edit_message_text(
                msg_choose_lang(user.lang),
                chat_id, mes_id,
                reply_markup=kb_params_choose_lang(user.lang)
            )

    if type == 'set_name':
        await bot.edit_message_text(
            msg_enter_nickname(user.lang), chat_id, mes_id,
            reply_markup=kb_user_params_back(user.lang)
        )
        await state.set(UserAccountState.nickname)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(UserAccountCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        user_account=user_account_factory.filter()
    )
