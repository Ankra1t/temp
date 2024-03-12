from telebot import TeleBot
from telebot.types import Message

from initialize import calcService
from db_new import db_new
from common.utils import digit_accept

from CALCULATE.states import StatsState
from CALCULATE.callbacks import kb_deal_profit_minus
from CALCULATE.common.messages import msg_calculate_result, msg_enter_profit_minus, msg_success_edit


def handle_new_currency(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_db_id = db_new.get_user_id_by_tg_id(user_id)

    chat_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        stat_id = data.get('stat_id', 0)

    value = digit_accept(message)
    if value is None:
        bot.send_message(
            chat_id, 'Ошибка!\n' + msg_enter_profit_minus(user_id),
            reply_markup=kb_deal_profit_minus(user_id, stat_id)
        )
        return

    calcService.set_profit(stat_id, -abs(value))

    calc_info = db_new.get_calculation(stat_id)
    if calc_info is None:
        return

    mes = msg_calculate_result(user_id, calc_info)
    mes += '\n\n✅ Расчет сохранен!'

    bot.send_message(chat_id, mes)
    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_new_currency, state=StatsState.loss)
