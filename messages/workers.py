from db_new import db_new


def admin_main_msg(count_all: int, count_with_sub: int, count_sub_more_1: int, count_admins: int, count_fut_post: int):
    return f"""🏠 <b></u>Главная</u></b>

В базе: {count_all}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}
Постоянные: {count_sub_more_1}
Количество администраторов: {count_admins}
Количество отложенных постов: {count_fut_post}
"""


def redactor_main_msg(count_fut: int):
    return f"Количество отложенных постов: {count_fut}"


def support_main_msg(count: int):
    return f"Количество заявок на поддержку: {count}"


def admin_users_msg(count_all: int, count_with_sub: int, count_sub_more_1: int):
    return f"""👨 <b><u>Пользователи</u></b>

В базе: {count_all}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}
Постоянные: {count_sub_more_1}
"""

def menu_msg(title: str):
    return f"""<b><u>{title}</u></b>

Действия:
"""

def admin_fut_posts_msg():
    posts_count = len(db_new.get_all_posts())

    return f"""📋 <b><u>Отложенные посты</u></b>

Количество: <b>{posts_count}</b>
"""


def admin_posting_msg(count: int):
    return f"""Отложенных постов: {count}"""
