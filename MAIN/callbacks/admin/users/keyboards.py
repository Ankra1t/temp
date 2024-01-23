from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import admin_users_factory

from initialize import kb_inl_admin


def getButton(text: str, type: str, filter='', page=1, client_id=0):
    return InlineKeyboardButton(text, None, admin_users_factory.new(
        type=type, filter=filter, client_id=client_id, page=page
    ))


def kb_admin_users():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Выдать подписку', 'put_subscribe')
    btn2 = getButton('Отменить подписку', 'cancel_subscribe')
    btn3 = getButton('Добавить/убавить', 'add_sub_subscribe')
    btn4 = getButton('Бан ⛔️', 'ban_list')
    btn5 = getButton('👨‍💻 Список клиентов', 'client_list', '', 1)
    btn6 = kb_inl_admin.go_main_btn

    # keyboard.add(btn1, btn2)
    # keyboard.add(btn3, btn4)
    keyboard.add(btn5, btn6)
    return keyboard


def kb_admin_users_list(pages: int, page: int, client_ids: list[int], filter=''):
    def getListButton(text: str, new_page: int, new_filter=None):
        new_filter = new_filter if (new_filter is not None) else filter
        return getButton(text, 'client_list', new_filter, new_page)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    btn_start = getListButton('В начало', 1)
    btn_end = getListButton('В конец', pages)
    btn_next = getListButton('Далее', page + 1)
    btn_back = getListButton('Назад', page - 1)

    counter = getButton(f'{page}/{pages}', 'counter')

    if pages > 1:
        if page == 1:
            keyboard.add(btn_end, counter, btn_next)
        elif page == pages:
            keyboard.add(btn_back, counter, btn_start)
        else:
            keyboard.add(btn_back, counter, btn_next)

    if filter == 'by_date_old':
        filter_text = 'Фильтрация: "сначала старые"'
        new_filter = 'by_paid'
    elif filter == 'by_paid':
        filter_text = 'Фильтрация: "сначала оплатившие"'
        new_filter = ''
    else:
        filter_text = 'Фильтрация: "сначала новые"'
        new_filter = 'by_date_old'

    btn_filter = getListButton(filter_text, 1, new_filter)
    keyboard.add(btn_filter)

    add_buttons: list[InlineKeyboardButton] = []
    for i, el in enumerate(client_ids):
        btn = getButton(f'{el}', 'client_info', '', 1, el)
        add_buttons.append(btn)

        if (len(add_buttons) == row_width) or (i + 1 == len(client_ids) and len(add_buttons) != 0):
            keyboard.add(*add_buttons)
            add_buttons = []

    keyboard.add(kb_inl_admin.go_users_btn, kb_inl_admin.go_main_btn)

    return keyboard


def kb_admin_client_info(client_id: int, is_banned: bool):
    def getClientButton(text: str, type: str):
        return getButton(text, type, '', 1, client_id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_ban = getClientButton(
        'Разбанить' if is_banned else 'Забанить', 'client_ban'
    )
    btn_remove_sub = getClientButton(
        'Отменить подписку', 'client_cancel_sub'
    )
    btn_add_sub = getClientButton(
        'Выдать подписку', 'client_add_sub'
    )

    keyboard.add(btn_add_sub, btn_remove_sub)
    keyboard.add(btn_ban, kb_inl_admin.go_users_btn)
    return keyboard


def kb_admin_users_confirm(type_info: str, client_id: int):
    def getConfimButton(text: str, type: str):
        return getButton(text, f'confirm_{type}_{type_info}', '', 1, client_id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_yes = getConfimButton('Да', 'yes')
    btn_no = getConfimButton('Нет', 'no')

    keyboard.add(btn_yes, btn_no)
    return keyboard


def kb_admin_users_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(kb_inl_admin.go_users_btn, kb_inl_admin.go_main_btn)
    return keyboard
