from telebot import TeleBot
from telebot.types import CallbackQuery

from Classes import base_statis

from states.admin_stats import AdminStatisticsState
from messages.statistics import admin_statistics_periods, admin_statistics_products

from .keyboards import kb_statistics_back, kb_stats_periods, kb_stats_products
from .filter import admin_statistics_factory, AdminStatisticsCallbackFilter
from ..pages import send_admin_main, send_admin_payment

def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data = admin_statistics_factory.parse(call.data)
    type = callback_data.get('type', '')
    filter = callback_data.get('filter', '')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'go_main':
        send_admin_main(bot, call.message, user_id)

    if type == 'go_payment':
        send_admin_payment(bot, call.message, user_id)

    if type == 'stat_pay_periods':

        # Посчитать продажи за периоды день, неделя, месяц
        count_today = base_statis.count_payments('today')
        count_week = base_statis.count_payments('week')
        count_month = base_statis.count_payments('month')
        count_half_year = base_statis.count_payments('half_year')
        count_year = base_statis.count_payments('year')

        summ_today = base_statis.summ_by_transactions('today')
        summ_week = base_statis.summ_by_transactions('week')
        summ_month = base_statis.summ_by_transactions('month')
        summ_half_year = base_statis.summ_by_transactions('half_year')
        summ_year = base_statis.summ_by_transactions('year')

        bot.edit_message_text(
            admin_statistics_periods(count_today, summ_today=summ_today,
                                     count_week=count_week, summ_week=summ_week,
                                     count_month=count_month, summ_month=summ_month,
                                     count_half_year=count_half_year, summ_half_year=summ_half_year,
                                     count_year=count_year, summ_year=summ_year
                                     ), chat_id, mes_id,
            reply_markup=kb_stats_periods()
        )
        pass

    elif type == 'stat_pay_products':

        # Вывести показатели
        count_signals = base_statis.count_by_product('signals')
        count_calc = base_statis.count_by_product('calc')
        count_calc_signals = base_statis.count_by_product('calc_signals')

        summ_signals = base_statis.summ_by_product('signals')
        summ_calc = base_statis.summ_by_product('calc')
        summ_calc_signals = base_statis.summ_by_product('calc_signals')


        bot.edit_message_text(
            admin_statistics_products(count_signals=count_signals, summ_signals=summ_signals,
                                      count_calc=count_calc, summ_calc=summ_calc,
                                      count_calc_signals=count_calc_signals, summ_calc_signals=summ_calc_signals
                                      ), chat_id, mes_id,
            reply_markup=kb_stats_products()
        )

    elif type == 'stat_pay_product_choose':

        clients_by_products = filter

        bot.edit_message_text(
            f'Список клиентов с платежами, по выбранному продукту:', chat_id, mes_id,
            reply_markup=None
        )
        base_statis.show_paid_users(bot, call.message, product=clients_by_products)
        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

    elif type == 'stat_pay_clients':
        bot.edit_message_text(
                'Список клиентов с платежами:', chat_id, mes_id,
                reply_markup=None
            )

        base_statis.show_paid_users(bot, call.message)

        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

    elif type == 'stat_pay_period_choose':
        clients_for_period = filter

        bot.edit_message_text(
            f'Список клиентов с платежами, за выбранный период:', chat_id, mes_id,
            reply_markup=None
        )
        base_statis.show_paid_users(bot, call.message, clients_for_period)
        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

    elif type == 'stat_pay_period_choose_start_date':

        bot.edit_message_text(
            'Введите дату начала в формате DD.MM.YY', chat_id, mes_id,
            reply_markup=kb_statistics_back()
        )

        bot.set_state(user_id, AdminStatisticsState.start_date_only, chat_id)

    elif type == 'stat_pay_period_choose_start_to_end':
        # Установить статус
        bot.edit_message_text(
            'Введите дату начала в формате dd.mm.yy:', chat_id, mes_id,
            reply_markup=kb_statistics_back()
        )

        bot.set_state(user_id, AdminStatisticsState.start_date, chat_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminStatisticsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_params=admin_statistics_factory.filter())


