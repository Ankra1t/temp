from telebot import TeleBot
from telebot.types import CallbackQuery

from db_new import db_new

# TODO удалить
from initialize import text_editor
from initialize import base_statis

from common.utils import set_state_data
from MAIN.states import AdminParamsState
from messages.statistics import admin_statistics_periods

from .keyboards import kb_statistics_back, kb_stats_periods
from .filter import admin_statistics_factory, AdminStatisticsCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = admin_statistics_factory.parse(call.data)
    type = callback_data['type']
    filter: str = callback_data.get('filter') or ''

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'stat_pay_periods':
        print(f'Нажато {type} ')

        # Посчитать продажи за периоды день, неделя, месяц
        count_today = base_statis.count_payments('today')
        count_week = base_statis.count_payments('week')
        count_month = base_statis.count_payments('month')
        count_half_year = base_statis.count_payments('half_year')
        count_year = base_statis.count_payments('year')
        # summ_all_users = base_statis.summ_by_transactions()
        bot.edit_message_text(
            admin_statistics_periods(count_today, summ_today=0,
                                     count_week=count_week, summ_week=0,
                                     count_month=count_month, summ_month=0,
                                     count_half_year=count_half_year, summ_half_year=0,
                                     count_year=count_year, summ_year=0
                                     ), chat_id, mes_id,
            reply_markup=kb_stats_periods()
        )
        pass

    elif type == 'stat_pay_products':
        print(f'Нажато {type} ')
        pass

    elif type == 'stat_pay_clients':
        print(f'Нажато {type} ')

        bot.edit_message_text(
                'Список клиентов с платежами:', chat_id, mes_id,
                reply_markup=None
            )

        base_statis.show_paid_users(call.message)
        # Установить статус
        # bot.edit_message_text(
        #     'Введите id или имя пользователя:', chat_id, mes_id,
        #     reply_markup=kb_statistics_back()
        # )

        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminStatisticsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_params=admin_statistics_factory.filter())
