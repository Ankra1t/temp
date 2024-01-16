from telebot.types import Message

def admin_main_msg(count_all: int, count_with_sub: int, count_sub_more_1: int, count_admins: int, count_fut_post: int):
    return f"""
<b>Главная</b>

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
    return f"""
<b>Пользователи</b>

В базе: {count_all}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}
Постоянные: {count_sub_more_1}
"""

def menu_msg(title: str):
    return f"""
<b>{title}</b>

Действия:
"""

# TODO - заменить на функцию выше
def admin_fut_posts_msg():
    return f"""
<b>Отложенные посты</b>

Действия:
"""


def admin_posting_msg(count: int):
    return f"""Отложенных постов: {count}"""


# TODO - вынести функцию в коммон
# Генерация нормального сообщения с Жирным, ссылкой и т.д.
def generate_normal_text(message: Message):
    msg_res = ''
    if message.content_type == 'photo' and message.caption_entities == None:
        return message.caption
    if message.content_type == 'text' and message.entities == None or message.text is None:
        return message.text
    if message.content_type == 'video' and message.caption_entities == None:
        return message.caption

    if message.content_type == 'text' and message.entities != None:
        msg_res = message.text
        for ent in message.entities:
            if ent.type == 'bold':
                serch = message.text[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<b>{serch}</b>')
                else:
                    msg_res = msg_res.replace(serch, f'<b>{serch}</b>')
            if ent.type == 'text_link':
                serch = message.text[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(
                        serch, f"<a href='{ent.url}'>{serch}</a>")
                else:
                    msg_res = msg_res.replace(
                        serch, f"<a href='{ent.url}'>{serch}</a>")
            if ent.type == 'underline':
                serch = message.text[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<u>{serch}</u>')
                else:
                    msg_res = msg_res.replace(serch, f'<u>{serch}</u>')
            if ent.type == 'italic':
                serch = message.text[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<i>{serch}</i>')
                else:
                    msg_res = msg_res.replace(serch, f'<i>{serch}</i>')
        return msg_res
    if message.content_type == 'photo' and message.caption_entities is not None and message.caption is not None:
        msg_res = message.caption
        for ent in message.caption_entities:
            if ent.type == 'bold':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<b>{serch}</b>')
                else:
                    msg_res = msg_res.replace(serch, f'<b>{serch}</b>')
            if ent.type == 'text_link':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(
                        serch, f"<a href='{ent.url}'>{serch}</a>")
                else:
                    msg_res = msg_res.replace(
                        serch, f"<a href='{ent.url}'>{serch}</a>")
            if ent.type == 'underline':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<u>{serch}</u>')
                else:
                    msg_res = msg_res.replace(serch, f'<u>{serch}</u>')
            if ent.type == 'italic':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<i>{serch}</i>')
                else:
                    msg_res = msg_res.replace(serch, f'<i>{serch}</i>')
        return msg_res
    if message.content_type == 'video' and message.caption_entities != None and message.caption is not None:
        msg_res = message.caption
        for ent in message.caption_entities:
            if ent.type == 'bold':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<b>{serch}</b>')
                else:
                    msg_res = msg_res.replace(serch, f'<b>{serch}</b>')
            if ent.type == 'text_link':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(
                        serch, f"<a href='{ent.url}'>{serch}</a>")
                else:
                    msg_res = msg_res.replace(
                        serch, f"<a href='{ent.url}'>{serch}</a>")
            if ent.type == 'underline':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<u>{serch}</u>')
                else:
                    msg_res = msg_res.replace(serch, f'<u>{serch}</u>')
            if ent.type == 'italic':
                serch = message.caption[ent.offset: ent.offset + ent.length]
                if '\n' in serch:
                    serch = serch.replace('\n', '')
                    msg_res = msg_res.replace(serch, f'<i>{serch}</i>')
                else:
                    msg_res = msg_res.replace(serch, f'<i>{serch}</i>')
        return msg_res
