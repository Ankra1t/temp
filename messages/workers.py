def admin_main_msg(
        count_all: int,
        count_with_sub: int,
        count_blocked: int,
        count_admins: int,
        count_fut_post: int,
        count_first_tries: int
):
    return f"""🏠 <b><u>Главная</u></b>

В базе: {count_all}
Заблокировали бота: {count_blocked}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}
Сделали тестовый расчёт: {count_first_tries}

Количество администраторов: {count_admins}
Количество отложенных постов: {count_fut_post}
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
