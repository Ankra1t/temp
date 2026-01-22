from threading import Timer
from telebot.async_telebot import AsyncTeleBot

from common.utils import edit_message
from services import auth
from config_logger import logger
from models import Message, StateContext, User

from messages.education import termins
from messages.enter import msg_choose_lang
from messages.profile import msg_referral, msg_site_login, msg_user_account
from messages.users import msg_start

from keyboards.settings import kb_choose_lang
from keyboards.account import kb_user_account, kb_user_referral
from keyboards.education import kb_user_education, kb_user_pages
from keyboards.user_main import kb_site_login, kb_user_main


async def send_user_main(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    new_user=False,
    is_first=False,
):
    # new_user=True
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    # if not new_user and message.text is not None and len(message.text.split()) == 2:
    #     _, code = message.text.split()
    #     if code == 'site':
    #         send_site_code(bot, message, user_id, True)
    #         return

    keyboard = kb_user_main(user.lang, new_user)

    if not new_user:
        text = msg_start(user.lang)

        if is_first:
            await bot.send_message(
                chat_id, text,
                reply_markup=keyboard
            )
        else:
            await bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )

    else:
        await bot.send_message(
            chat_id, msg_choose_lang(user.lang),
            reply_markup=kb_choose_lang(user.lang, True)
        )


async def send_user_education(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    await bot.edit_message_text(
        'Обучение', chat_id, mes_id,
        reply_markup=kb_user_education()
    )


async def send_user_terms(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    page: int,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    await bot.edit_message_text(
        termins[page - 1], chat_id, mes_id, parse_mode='Markdown',
        reply_markup=kb_user_pages(page, len(termins))
    )


async def send_user_account(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False,
):
    chat_id = message.chat.id

    await state.delete()

    # TODO: получить количество рефералов через API
    # ref_user = user_service.getReferralOfUser(user.id)
    # referals = ref_user.refsCount if ref_user else 0
    referals = 0

    text = msg_user_account(user.lang, referals)
    keyboard = kb_user_account(user.lang, user.tgId)

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await edit_message(
            bot, message, 'text', text, keyboard
        )


async def send_site_code(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_reset=False,
    prev_code='',
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    if message.text:
        _, param = message.text.split()
        if '_' in param:
            _, code = param.split('_')
            auth.send_site_code(userId=user.id, code=code)
            await bot.send_message(
                chat_id, '✅ Вы успешно авторизированны.\nВозвращайтесь на сайт, чтобы продолжить работу.'
            )
            return

    new_code = prev_code or auth.get_site_code(userId=user.id)

    text = msg_site_login(user.lang)
    keyboard = kb_site_login(user.lang, new_code or '', is_reset)

    try:
        if is_first:
            new_message = await bot.send_message(
                chat_id, text,
                reply_markup=keyboard
            )
        else:
            new_message = message
            await bot.edit_message_text(
                text,
                chat_id, mes_id,
                reply_markup=keyboard
            )

        if is_reset:
            code = new_code or ''

            async def get_default():
                await send_site_code(
                    bot, new_message, state, user,  # type: ignore
                    False, code, False,
                )

            Timer(3, get_default).start()
    except:
        logger.error('[send_site_code]: сообщение не изменено!')


async def send_referral(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    # TODO: получить количество рефералов через API
    # ref_user = user_service.getReferralOfUser(user.id)
    # referals_count = ref_user.refsCount if ref_user else 0
    referals_count = 0

    text = msg_referral(user.lang, referals_count, (await bot.get_me()).username or '', user.id)
    kb = kb_user_referral(user.lang, referals_count)

    if is_first:
        await bot.send_message(chat_id, text, reply_markup=kb)
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb
        )


async def send_user_params(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    user: User,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    # TODO: получить данные пользователя через API
    # Временно скрываем эту функциональность
    await bot.send_message(
        chat_id, 'Функция в разработке'
    )
