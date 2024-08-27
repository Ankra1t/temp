from telebot import TeleBot
from telebot.types import CallbackQuery

from config_logger import logger
from db import db
from services import calculation, violation

from common.utils import delete_message, get_lang
from common.calc_step import send_calc_start

from callbacks.stats import send_week_stats
from keyboards.stats import kb_calc_result
from keyboards.main import main_factory, MainCallbackFilter
from pages.calculate import send_admin_channel_calc_list, send_channel_post, send_manual, send_settings, send_main, send_stats, send_tariffs_list_item, send_violation


def _main_callback_handler(call: CallbackQuery, bot: TeleBot):
    callback_data = main_factory.parse(call.data)
    type = callback_data.get('type', '')
    is_saved = callback_data.get('is_saved', 'False')
    stat_id = int(callback_data.get('stat_id', -1))

    user_id = call.from_user.id
    user_db_id = db.get_user_id_by_tg_id(user_id)
    lang = get_lang(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    is_rus = call.from_user.language_code == 'ru'

    logger.info(
        f'callback "main_factory" user_tg_id={user_id} type={type} stat_id={stat_id} saved={is_saved}'
    )

    if 'calc' in type or type == 'settings' or type == 'calc_stats':
        calc = calculation.get(stat_id)
        if calc is not None:
            bot.edit_message_reply_markup(
                chat_id, mes_id,
                reply_markup=kb_calc_result(lang, user_db_id, calc)
            )
        else:
            delete_message(bot, chat_id, mes_id)

    if 'calc' in type:
        send_calc_start(
            bot, call.message, user_id,
            is_continue='_continue' in type, is_channel_calc='ch_calc' in type
        )

    if type == 'first_try':
        send_calc_start(
            bot, call.message, user_id,
            is_continue='_continue' in type, is_edit=True, is_try=True
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

    if type == 'week_stat':
        send_week_stats(bot)
        send_week_stats(bot, 652)

    if type == 'channels':
        send_admin_channel_calc_list(bot, call.message, user_id)

    if type == 'channel_post':
        send_channel_post(bot, call.message, user_id)

    if type == 'info':
        send_manual(bot, call.message, user_id)

    if 'violation+' in type:
        result = False if '+no' in type else True if '+yes' in type else None
        violation.create(user_db_id, result)
        type = 'violations'

    if 'violation_edit+' in type:
        today_violation = violation.getToday(user_db_id)
        if today_violation:
            result = False if '+no' in type else True if '+yes' in type else 'null'
            violation.update(today_violation.get('id', 0), status=result)
            type = 'violations'

    if type == 'violation_edit':
        send_violation(bot, call.message, user_id, is_edit=True)

    if type == 'violations':
        send_violation(bot, call.message, user_id)

    # if type == 'violation_yes':
    #     data = violation.create(user_db_id, True)
    #     if data is not None:
    #         id = data.get('id')

    #         bot.edit_message_text(
    #             msg_violation_message(user_id),
    #             chat_id, mes_id,
    #             reply_markup=kb_violation_skip(user_id)
    #         )
    #         bot.set_state(user_id, ViolationState.message, chat_id)
    #         set_state_data(
    #             bot, user_id, chat_id,
    #             {
    #                 'del_mes_id': mes_id,
    #                 'violation_id': id
    #             }
    #         )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter()
    )
