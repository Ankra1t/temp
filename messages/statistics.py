from telebot.types import Message




def admin_main_statistics(count_subscribes=0, summ_all_users=0 ):
    return f"""
<b>Общая статистика продаж:</b>

Кол-во подписок куплено: {count_subscribes} шт
Получена сумма по всем подпискам: {summ_all_users} USDT


Смотреть подробнее:
"""

def admin_statistics_periods(count_today=0, summ_today=0,
                             count_week=0, summ_week=0,
                             count_month=0, summ_month=0,
                             count_half_year=0, summ_half_year=0,
                             count_year=0, summ_year=0
                             ):
    return f"""
<b>Продажи по периодам:</b>

За сутки: {count_today} шт, сумма {summ_today} USDT
За неделю: {count_week} шт, сумма {summ_week} USDT
За месяц: {count_month} шт, сумма {summ_month} USDT
За 6 месяцев: {count_half_year} шт, сумма {summ_half_year} USDT
За 1 год: {count_year} шт, сумма {summ_year} USDT

Смотреть клиентов за выбранный период:
"""