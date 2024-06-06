def admin_main_msg(
        count_all: int,
        count_with_sub: int,
        count_blocked: int,
        count_admins: int,
        count_today_users: int,
        count_first_tries: int,
        count_refs: int
):
    return f"""🏠 <b><u>Главная</u></b>

В базе: {count_all}
Заблокировали бота: {count_blocked}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}

Зарегестрировались сегодня: {count_today_users}
Из них провели тестовый расчёт: {count_first_tries}

Количество администраторов: {count_admins}
Количество по рефералке: {count_refs}
"""


def admin_users_msg(count_all: int, count_with_sub: int, count_blocked: int):
    return f"""👨 <b><u>Пользователи</u></b>

В базе: {count_all}
Заблокировали бота: {count_blocked}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}
"""


def menu_msg(title: str):
    return f"""<b><u>{title}</u></b>

Действия:
"""


def admin_fut_posts_msg(posts_count: int):
    return f"""📋 <b><u>Отложенные посты</u></b>

Количество: <b>{posts_count}</b>
"""
