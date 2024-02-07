from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db
from db_new import db_new

# TODO удалить
from initialize import text_editor
from initialize import base_statis

from common.utils import set_state_data
from MAIN.states import AdminParamsState
from messages.statistics import admin_statistics_periods, admin_statistics_products

from .keyboards import kb_statistics_back, kb_stats_periods, kb_stats_products
from .filter import admin_statistics_factory, AdminStatisticsCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = admin_statistics_factory.parse(call.data)
    type = callback_data['type']
    filter: str = callback_data.get('filter') or ''

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

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


        bot.edit_message_text(
            admin_statistics_products(), chat_id, mes_id,
            reply_markup=kb_stats_products()
        )

    elif type == 'stat_pay_product_choose':
        clients_by_products = filter
        bot.edit_message_text(
            f'Оплат по продукту не обнаружено', chat_id, mes_id,
            reply_markup=None
        )
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

        base_statis.show_paid_users(call.message)
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
        base_statis.show_paid_users(call.message, clients_for_period)
        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

    elif type == 'stat_pay_period_choose_start_date':
        print(f'Нажато {type} ')

        # Установить статус
        bot.edit_message_text(
            'Введите дату начала в формате dd.mm.yy:', chat_id, mes_id,
            reply_markup=kb_statistics_back()
        )

    elif type == 'stat_pay_period_choose_start_to_end':
        print(f'Нажато {type} ')

        # Установить статус
        bot.edit_message_text(
            'Введите дату начала в формате dd.mm.yy:', chat_id, mes_id,
            reply_markup=kb_statistics_back()
        )


    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminStatisticsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_params=admin_statistics_factory.filter())
