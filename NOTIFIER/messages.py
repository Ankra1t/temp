
def mess_set_trial_subsctibe_new_user(user_id: int, user_nike='', days=0):
    return f"""
<b>Назначена пробный доступ:</b>

Новому пользователю c db_id {user_id} ({user_nike}) назначен пробный доступ на {days}дн.
"""