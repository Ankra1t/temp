from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.callbacks.main.keyboards import kb_menu_back
from CALCULATE.callbacks.stats.handler import send_week_stats
from config_logger import logger
from common.utils import delete_message
from db import db

from ..stats.keyboards import kb_calc_result
from ..utils import send_calc_start
from ..pages import send_admin_channel_calc_list, send_channel_post, send_settings, send_main, send_stats, send_tariffs_list_item
from .filter import main_factory, MainCallbackFilter


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
        send_calc_start(bot, call.message, user_id,
                        is_continue='_continue' in type, is_channel_calc='ch_calc' in type)

    if type == 'first_try':
        send_calc_start(bot, call.message, user_id,
                        is_continue='_continue' in type, is_edit=True, is_try=True)

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
        bot.edit_message_text("""<b>Для чего калькулятор? </b>

Если Вы когда-нибудь слышали слово "риск-менеджмент", то это именно тот самый инструмент, позволяющий управлять капиталом.

Калькулятор для расчета ваших <b>убытков</b> <b>и</b> <b>прибыли</b>.

 Работает элементарно.

Вписываете свой депозит, сумму или процент от капитала, который готовы "потерять" в сделке, а <b>калькулятор</b> высчитывает <b>количество</b> монет/акций/лотов (в зависимости от рынка) для покупки.

<b>Вот пример. </b>

У меня есть баланс в 10 000 долларов.

<b>1 условие: </b>

Я хочу купить Биткоин по цене 66 000 долларов.

<b>2 условие: </b>

Моя цена стоп-лосс пусть будет 65850 (вот так я решил, что ниже этой цены упасть не дам)

<b>3 условие: </b>

Я готов от <b>10 000 USDT</b> депозита зафиксировать убыток в <b>100 USDT</b> (стоп-лосс)

Вопрос, сколько нужно купить монет, чтобы в убыточном случае депозит остался в размере 9900 USDT?

<b>4 условие: </b>

Ввожу данные в калькулятор и идет автоматически расчет, где мне нужно по цене 66 000 купить 0.7909 монет, а при цене 65873.56 выставить свой стоп-лосс (и тогда потеря суммы будет не более 100 USDT)

А при цене <b>66379.32</b> прибыль со сделки уже составит <b>+300</b> <b>USDT </b>

Итог: вот как работают профессионалы, от сделки до сделки.
Трейдинг - это не казино, а расчеты и системный подход.

Информация дополняется.""", chat_id, mes_id, reply_markup=kb_menu_back(user_id))

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(MainCallbackFilter())
    bot.register_callback_query_handler(
        _main_callback_handler,
        lambda _: True, pass_bot=True,
        main=main_factory.filter()
    )
