from telebot.async_telebot import AsyncTeleBot
from telebot.util import extract_arguments

from config_logger import logger
from service.user_settings_storage import user_settings_storage
from messages.main import msg_support
from models import LANGUAGES, Message, StateContext, User

from common.utils import is_digit
from common.calc_step import send_calc_start

from pages.calculate import send_admin_channel_calc_list, send_channel_post, send_main, send_manual_page, send_settings
from pages.user import send_referral
from pages.start import send_start_by_user

from keyboards.account import kb_support


async def _start(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    user_role = 0
    is_registered = False
    quick_calc_tool = None
    quick_calc_price = None
    quick_calc_stop = None

    # Проверяем реферальный id или быстрый запуск калькулятора
    mes_args = extract_arguments(message.text or '')

    if mes_args is not None:
        # Проверяем формат монета_цена для быстрого запуска калькулятора
        if mes_args.startswith('l_'):
            parts = mes_args.split('_')
            try:
                if len(parts) == 4:
                    _, tool_part, price_part, float_part = parts
                    # Проверяем, что price_part - число (может быть дробным)
                    quick_calc_price = float(f'{price_part}.{float_part or 0}')
                    quick_calc_tool = tool_part  # например, BTCUSDT

                if len(parts) == 6:
                    _, tool_part, price_part, float_part, stop_part, stop_float = parts
                    # Проверяем, что price_part - число (может быть дробным)
                    quick_calc_price = float(f'{price_part}.{float_part or 0}')
                    quick_calc_tool = tool_part  # например, BTCUSDT
                    quick_calc_stop = float(f'{stop_part}.{stop_float or 0}')
            except ValueError:
                # Если не число, проверяем на ref_id
                if is_digit(mes_args):
                    ref_id = int(mes_args)
        elif is_digit(mes_args):
            ref_id = int(mes_args)

    if user_role is None:
        ref_id = None

        username = message.from_user.username

        # TODO - Регистрация?
        # is_registered = auth.registration(
        #     userId=user.tgId,
        #     username=username,
        #     referId=ref_id
        # )

        new_user = None  # TODO - изменить логику с проверкой из API

        if new_user is not None and is_registered == True:
            logger.info(
                f'/auth/tg_register [tg_id={user.tgId} @{username}]'
            )

            # TODO - кол-во пользователей за сегодня
            num = 0

            # Проверка языка
            user_lang = (message.from_user.language_code or 'en').lower()
            lang = user_lang if (user_lang in LANGUAGES) else 'en'
            user_settings_storage.set_lang(user.tgId, lang)

            # Уведомление о регистрации
            # sentMessages = await notifier.send_user_is_registered(
            #     new_user.id, num
            # )

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
        quick_calc_tool=quick_calc_tool,
        quick_calc_price=quick_calc_price,
        quick_calc_stop=quick_calc_stop,
    )


async def _calc(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_main(bot, message, state, user, True)


async def _faq(message: Message, bot: AsyncTeleBot, state: StateContext):
    msg = '*Ошибка*'

    await bot.send_message(message.chat.id, msg)
    await state.delete()


async def _about_us(message: Message, bot: AsyncTeleBot, state: StateContext):
    msg = '*Ошибка*'

    await bot.send_message(message.chat.id, msg)
    await state.delete()


async def _support(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    sup = 'calcsup'
    msg = msg_support(user.lang)

    await bot.send_message(
        message.chat.id, msg,
        reply_markup=kb_support(user.lang, sup)
    )
    await state.delete()


async def _manual(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    await send_manual_page(bot, message, state, user, 1, True)


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
    pass


def commands_registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

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
