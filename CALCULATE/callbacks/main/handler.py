from telebot import TeleBot
from telebot.types import CallbackQuery

from config_logger import logger
from common.utils import delete_message
from db import db

from ..stats.keyboards import kb_calc_result
from .filter import main_factory, MainCallbackFilter
from ..utils import choose_first_calculate_step
from ..pages import send_settings, send_main, send_stats, send_tariffs_list_item


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')
    is_saved = callback_data.get('is_saved', 'False')
    stat_id = int(callback_data.get('stat_id', -1))

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id
    user_db_id = db.get_user_id_by_tg_id(user_id)

    is_rus = call.from_user.language_code == 'ru'

    logger.info(
        f'callback "main_factory" user_tg_id={user_id} type={type} stat_id={stat_id} saved={is_saved}'
    )

    if 'calc' in type or type == 'settings':
        if stat_id != -1:
            bot.edit_message_reply_markup(
                chat_id, mes_id,
                reply_markup=kb_calc_result(
                    user_id, stat_id, is_saved == 'True'
                )
            )
        else:
            delete_message(bot, chat_id, mes_id)

    if 'calc' in type:
        u_base = db.get_calc_user_settings(user_db_id)
        market = u_base.market if (u_base is not None) else 'crypto'

        choose_first_calculate_step(
            bot, user_id, call.message, market, False, '_continue' in type
        )

    if type == 'settings':
        send_settings(bot, call.message, user_id, True)

    if type == 'go_main':
        send_main(call.message, bot, user_id)

    if type == 'stats':
        send_stats(bot, call.message, user_id)

    if type == 'buy':
        send_tariffs_list_item(
            bot, call.message, user_id, 'calc', 0, is_rus=is_rus
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter()
    )
