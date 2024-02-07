from statistics import median_low
from telebot import TeleBot
from telebot.types import CallbackQuery
from CALCULATE.callbacks.utils import choose_calculate_step

from common.utils import set_state_data

from CALCULATE.states.calculate import CalculateState
from CALCULATE.callbacks import kb_cancel, kb_forex_val


# ======================= // ANCHOR Переменные

# FOREX Текущий курс (USDUSD)
# curs = 0
# def user_get_curs(bot: TeleBot):
#     def r_func(message: Message):
#         global curs
#         flag = True
#         try:
#             input_calc = message.text
#             input_calc = input_calc.replace(' ', '')
#             input_calc = float(input_calc)
#         except:
#             flag = False
#         if flag:
#             curs = input_calc
#             bot.send_message(
#                 message.chat.id, 'Введите цену стоп лосса:', reply_markup=kb_cancel(user_id))
#             bot.register_next_step_handler(message, user_get_sl_forex(bot))
#         else:
#             bot.send_message(
#                 message.chat.id, 'Ошибка - введите число', reply_markup=kb_cancel(user_id))
#             bot.register_next_step_handler(message, user_get_curs(bot))
#     return r_func


# =============================== //ANCHOR - Обработка INLINE
def callback_inline(call: CallbackQuery, bot: TeleBot):
    type = call.data

    mes_id = call.message.id
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if type == 'RUB' or type == 'USD':
        set_state_data(bot, user_id, chat_id, {'val_dep': type})
        bot.edit_message_text(
            'Введите размер депозита:', chat_id, mes_id,
            reply_markup=kb_cancel(user_id)
        )
        choose_calculate_step(bot, user_id, chat_id, mes_id, True)

    if type == 'DOP':
        # forex = [{"pair": "AUD/CAD", "price": "0", "help_pair": "USD/CAD"},
        #          {"pair": "AUD/CHF", "price": "0", "help_pair": "USD/CHF"},
        #          {"pair": "AUD/JPY", "price": "0", "help_pair": "USD/JPY"},
        #          {"pair": "CAD/CHF", "price": "0", "help_pair": "USD/CHF"},
        #          {"pair": "CAD/JPY", "price": "0", "help_pair": "USD/JPY"},
        #          {"pair": "CHF/JPY", "price": "0", "help_pair": "USD/JPY"},
        #          {"pair": "EUR/AUD", "price": "0", "help_pair": "AUD/USD"},
        #          {"pair": "EUR/CAD", "price": "0", "help_pair": "USD/CAD"},
        #          {"pair": "EUR/CHF", "price": "0", "help_pair": "USD/CHF"},
        #          {"pair": "EUR/GBP", "price": "0", "help_pair": "GBP/USD"},
        #          {"pair": "EUR/JPY", "price": "0", "help_pair": "USD/JPY"},
        #          {"pair": "EUR/NZD", "price": "0", "help_pair": "NZD/USD"},
        #          {"pair": "GBP/AUD", "price": "0", "help_pair": "AUD/USD"},
        #          {"pair": "GBP/CAD", "price": "0", "help_pair": "USD/CAD"},
        #          {"pair": "GBP/CHF", "price": "0", "help_pair": "USD/CHF"},
        #          {"pair": "GBP/JPY", "price": "0", "help_pair": "USD/JPY"},
        #          {"pair": "GBP/NZD", "price": "0", "help_pair": "NZD/USD"},
        #          {"pair": "NZD/CAD", "price": "0", "help_pair": "USD/CAD"},
        #          {"pair": "NZD/CHF", "price": "0", "help_pair": "USD/CHF"},
        #          {"pair": "NZD/JPY", "price": "0", "help_pair": "USD/JPY"},
        #          {"pair": "NZD/USD", "price": "0.62625", "help_pair": ""},
        #          {"pair": "GBP/USD", "price": "1.2936", "help_pair": ""},
        #          {"pair": "EUR/USD", "price": "1.12044", "help_pair": ""},
        #          {"pair": "AUD/USD", "price": "0.677", "help_pair": ""},
        #          {"pair": "USD/JPY", "price": "139.608", "help_pair": ""},
        #          {"pair": "USD/CHF", "price": "0.85793", "help_pair": ""},
        #          {"pair": "USD/CAD", "price": "1.31632", "help_pair": ""},
        #          {"pair": "USD/RUB", "price": "91.9445", "help_pair": ""}]
        # for el in forex:
        #     db_new.update_forex(el['pair'], float(el['price']), el['help_pair'])

        # db_new.delete_calculator_user(user_id)
        pass

    bot.answer_callback_query(call.id)
