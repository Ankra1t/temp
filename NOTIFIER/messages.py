def mess_user_paid(user_id, user_nike, summ_paid, tariff_name, finish_date):
    return f"""
<b>Пользователь оплатил абонемент:</b>

Пользователь db_id {user_id} ({user_nike}) оплатил за {summ_paid} абонемент "{tariff_name}" до {finish_date}.
    """
