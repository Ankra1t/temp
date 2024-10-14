from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from CHANNEL.channel_post import channel_post
from config_logger import logger
from services import calculation, violation
from models import CallbackQuery, StateContext, User

from common.utils import delete_message
from common.calc_step import send_calc_start

from keyboards.stats import kb_calc_result
from keyboards.main import main_factory, MainCallbackFilter
from pages.calculate import send_admin_channel_calc_list, send_channel_post, send_manual, send_settings, send_main, send_stats, send_tariffs_list_item, send_violation


async def _main_callback_handler(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')
    is_saved = callback_data.get('is_saved', 'False')
    stat_id = int(callback_data.get('stat_id', -1))

    chat_id = call.message.chat.id
    mes_id = call.message.id

    is_rus = call.from_user.language_code == 'ru'

    logger.info(
        f'callback "main_factory" user_tg_id={user.tgId} type={type} stat_id={stat_id} saved={is_saved}'
    )

    if 'calc' in type or type == 'settings':
        calc = calculation.get(stat_id)
        if calc is not None:
            try:
                await bot.edit_message_reply_markup(
                    chat_id, mes_id,
                    reply_markup=kb_calc_result(user.lang, user.id, calc)
                )
            except:
                pass
        else:
            await delete_message(bot, chat_id, mes_id)

    if 'calc' in type:
        await send_calc_start(
            bot, call.message, state, user,
            is_continue='_continue' in type, is_channel_calc='ch_calc' in type
        )

    if type == 'first_try':
        await send_calc_start(
            bot, call.message, state, user,
            is_continue='_continue' in type, is_edit=True, is_try=True
        )

    if type == 'settings':
        await send_settings(bot, call.message, state, user, True)

    if type == 'go_main':
        await send_main(bot, call.message, state, user)

    if type == 'stats':
        await send_stats(bot, call.message, state, user)

    if type == 'buy':
        await send_tariffs_list_item(
            bot, call.message, state, user, 'calc', 0, is_rus=is_rus
        )

    if type == 'week_stat':
        await channel_post.send_stats()

    if type == 'channels':
        await send_admin_channel_calc_list(bot, call.message, state)

    if type == 'channel_post':
        await send_channel_post(bot, call.message, state)

    if type == 'info':
        await send_manual(bot, call.message, state, user)

    if 'violation+' in type:
        result = False if '+no' in type else True if '+yes' in type else None
        violation.create(user.id, result)
        type = 'violations'

    if 'violation_edit+' in type:
        today_violation = violation.getToday(user.id)
        if today_violation:
            result = False if '+no' in type else True if '+yes' in type else 'null'
            violation.update(today_violation.get('id', 0), status=result)
            type = 'violations'

    if type == 'violation_edit':
        await send_violation(bot, call.message, state, user, is_edit=True)

    if type == 'violations':
        await send_violation(bot, call.message, state, user)

    if type == 'active':
        pass

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,  # type: ignore
        lambda _: True, pass_bot=True,
        main=main_factory.filter()
    )
