from statistics import median_low
from telebot import TeleBot
from telebot.types import CallbackQuery
from CALCULATE.callbacks.utils import choose_calculate_step

from db import db
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
        # forex = [{"paire": "AUD/CAD", "price": "0", "help_paire": "USD/CAD"},
        #          {"paire": "AUD/CHF", "price": "0", "help_paire": "USD/CHF"},
        #          {"paire": "AUD/JPY", "price": "0", "help_paire": "USD/JPY"},
        #          {"paire": "CAD/CHF", "price": "0", "help_paire": "USD/CHF"},
        #          {"paire": "CAD/JPY", "price": "0", "help_paire": "USD/JPY"},
        #          {"paire": "CHF/JPY", "price": "0", "help_paire": "USD/JPY"},
        #          {"paire": "EUR/AUD", "price": "0", "help_paire": "AUD/USD"},
        #          {"paire": "EUR/CAD", "price": "0", "help_paire": "USD/CAD"},
        #          {"paire": "EUR/CHF", "price": "0", "help_paire": "USD/CHF"},
        #          {"paire": "EUR/GBP", "price": "0", "help_paire": "GBP/USD"},
        #          {"paire": "EUR/JPY", "price": "0", "help_paire": "USD/JPY"},
        #          {"paire": "EUR/NZD", "price": "0", "help_paire": "NZD/USD"},
        #          {"paire": "GBP/AUD", "price": "0", "help_paire": "AUD/USD"},
        #          {"paire": "GBP/CAD", "price": "0", "help_paire": "USD/CAD"},
        #          {"paire": "GBP/CHF", "price": "0", "help_paire": "USD/CHF"},
        #          {"paire": "GBP/JPY", "price": "0", "help_paire": "USD/JPY"},
        #          {"paire": "GBP/NZD", "price": "0", "help_paire": "NZD/USD"},
        #          {"paire": "NZD/CAD", "price": "0", "help_paire": "USD/CAD"},
        #          {"paire": "NZD/CHF", "price": "0", "help_paire": "USD/CHF"},
        #          {"paire": "NZD/JPY", "price": "0", "help_paire": "USD/JPY"},
        #          {"paire": "NZD/USD", "price": "0.62625", "help_paire": ""},
        #          {"paire": "GBP/USD", "price": "1.2936", "help_paire": ""},
        #          {"paire": "EUR/USD", "price": "1.12044", "help_paire": ""},
        #          {"paire": "AUD/USD", "price": "0.677", "help_paire": ""},
        #          {"paire": "USD/JPY", "price": "139.608", "help_paire": ""},
        #          {"paire": "USD/CHF", "price": "0.85793", "help_paire": ""},
        #          {"paire": "USD/CAD", "price": "1.31632", "help_paire": ""},
        #          {"paire": "USD/RUB", "price": "91.9445", "help_paire": ""}]
        # for el in forex:
        #     db.add_forex(el['paire'], float(el['price']), el['help_paire'])

        # db.delete_calculator_user(user_id)

        # print(db.get_all_forex_btn())
        pass

    bot.answer_callback_query(call.id)
