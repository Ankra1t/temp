from telebot.types import Message


def admin_main_statistics(count_subscribes=0, summ_all_users=0 ):
    return f"""<b><u>Общая статистика продаж</u></b>

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
    return f"""<b><u>Продажи по периодам</u></b>

За сутки:  <b>{count_today} шт</b>, сумма <b>{summ_today} USDT</b>
За неделю: <b>{count_week} шт</b>,  сумма <b>{summ_week} USDT</b>
За месяц:  <b>{count_month} шт</b>, сумма <b>{summ_month} USDT</b>
За 6 мес.: <b>{count_half_year} шт</b>, сумма <b>{summ_half_year} USDT</b>
За 1 год:  <b>{count_year} шт</b>, сумма <b>{summ_year} USDT</b>

Смотреть клиентов за выбранный период:
"""


def admin_statistics_products(count_signals=0, summ_signals=0,
                             count_calc=0, summ_calc=0,
                             count_calc_signals=0, summ_calc_signals=0
                             ):
    return f"""<b><u>Продажи по продуктам</u></b>

Продукт "Сигналы":  <b>{count_signals} шт</b>, сумма <b>{summ_signals} USDT</b>
Продукт "Калькулятор":  <b>{count_calc} шт</b>, сумма <b>{summ_calc} USDT</b>
Продукт "Калькулятор+сигналы":  <b>{count_calc_signals} шт</b>, сумма <b>{summ_calc_signals} USDT</b>

Смотреть клиентов по выбранному продукту:
    """