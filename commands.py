from telebot.async_telebot import AsyncTeleBot
from telebot.util import extract_arguments

from config_logger import logger
from AuthRoles import check_registration
from NOTIFIER import notifier
from db import db
from messages.main import msg_support
from models import LANGUAGES, Message, StateContext, User
from services import auth

from common.utils import is_digit
from common.calc_step import send_calc_start

from pages.calculate import send_admin_channel_calc_list, send_channel_post, send_main, send_manual_page, send_settings
from pages.user import send_referral, send_site_code
from pages.start import send_start_by_user

from keyboards.account import kb_support


async def _start(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    user_role = check_registration(user.tgId)
    is_registered = False

    if user_role is None:
        # Проверяем реферальный id
        mes_args = extract_arguments(message.text or '')

        ref_id = None
        if mes_args is not None and is_digit(mes_args):
            ref_id = int(mes_args)

        username = message.from_user.username

        is_registered = auth.registration(user.tgId, username, ref_id)
        new_user = db.get_user_by_tg_id(user.tgId)

        if new_user is not None and is_registered == True:
            logger.info(
                f'/auth/tg_register [tg_id={user.tgId} @{username}]'
            )

            num = len(db.get_today_users())

            # Проверка языка
            user_lang = (message.from_user.language_code or 'en').lower()
            lang = user_lang if (user_lang in LANGUAGES) else 'en'
            db.set_user_lang(new_user.id, lang)

            # Уведомление о регистрации
            sentMessages = await notifier.send_user_is_registered(
                new_user.id, num
            )

            if sentMessages:
                auth.addUserNotificationMessages(
                    new_user.id, sentMessages, user_lang, num
                )

            is_registered = True
        else:
            logger.error(
                f'Ошибка регистрации пользователя tg_id={user.tgId} @{username}'
            )

    await send_start_by_user(
        bot,
        message,
        state,
        user,
        is_registered or False,
    )


async def _calc(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_main(bot, message, state, user, True)


async def _teststart(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    user_id = message.from_user.id

    user_db_id = db.get_user_id_by_tg_id(user_id)
    db.set_calculator_user_market(user_db_id, 'crypto')

    await send_start_by_user(
        bot,
        message,
        state,
        user,
        True,
    )


async def _faq(message: Message, bot: AsyncTeleBot, state: StateContext):
    text = db.get_text_by_name('FAQ')
    msg = text.message if (text is not None) else '*Ошибка*'

    await bot.send_message(message.chat.id, msg)
    await state.delete()


async def _about_us(message: Message, bot: AsyncTeleBot, state: StateContext):
    text = db.get_text_by_name('О нас')
    msg = text.message if (text is not None) else '*Ошибка*'

    await bot.send_message(message.chat.id, msg)
    await state.delete()


async def _support(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    sup = db.get_support_name()
    msg = msg_support(user.lang)

    await bot.send_message(
        message.chat.id, msg,
        reply_markup=kb_support(user.lang, sup)
    )
    await state.delete()


async def _manual(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_manual_page(bot, message, state, user, 1, True)


async def _site(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_site_code(bot, message, state, user, is_first=True)


async def _settings(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_settings(bot, message, state, user, True)


async def _calc_start(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_calc_start(bot, message, state, user)


async def _channel_calc(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    if user.role != 1:
        return

    await send_calc_start(bot, message, state, user, is_channel_calc=True)


async def _referral(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_referral(bot, message, state, user, True)


async def _channel_post(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    if user.role != 1:
        return

    await send_channel_post(bot, message, state, True)


async def _results(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    if user.role != 1:
        return

    await send_admin_channel_calc_list(bot, message, state, is_first=True)


async def _test(message: Message, bot: AsyncTeleBot):
    # print(1)

    # await asyncio.sleep('5')

    # print(2)
    pass


def commands_registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(_teststart, commands=['teststart'])

    reg_mes(_start, commands=['start'])

    reg_mes(_faq, commands=['faq'])
    reg_mes(_about_us, commands=['about_us'])

    reg_mes(_support, commands=['support'])
    reg_mes(_support, commands=['team'])

    reg_mes(_manual, commands=['manual'])

    reg_mes(_calc, commands=['menu'])
    reg_mes(_settings, commands=['settings'])
    reg_mes(_calc_start, commands=['calc'])
    reg_mes(_calc_start, commands=['calculator'])
    reg_mes(_channel_calc, commands=['channel_calc'])

    reg_mes(_channel_post, commands=['channels'])
    reg_mes(_results, commands=['d'])

    reg_mes(_referral, commands=['referral'])

    reg_mes(_test, commands=['test11'])

    bot.register_channel_post_handler(_test, pass_bot=True)  # type: ignore
