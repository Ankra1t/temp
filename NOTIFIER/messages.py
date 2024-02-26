
def mess_set_trial_subsctibe_new_user(user_id: int, user_nike='', days=0):
    return f"""
<b>Назначен пробный доступ:</b>

Новому пользователю c db_id {user_id} ({user_nike}) назначен пробный доступ на {days}дн.
"""

def mess_user_paid(user_id, user_nike, summ_paid, tariff_name, finish_date):
    return f"""
<b>Пользователь оплатил абонемент:</b>

Пользователь db_id {user_id} ({user_nike}) оплатил за {summ_paid} абонемент "{tariff_name}" до {finish_date}.
    """