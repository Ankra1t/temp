from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import admin_users_factory

from initialize import kb_inl_admin


def getButton(text: str, type: str, filter='', page=1, client_db_id=0):
    return InlineKeyboardButton(text, None, admin_users_factory.new(
        type=type, filter=filter, client_db_id=client_db_id, page=page
    ))


def kb_admin_users():
    keyboard = InlineKeyboardMarkup(row_width=2)

    ban = getButton('⛔️ Бан', 'ban_list')
    search = getButton('🔎 Поиск пользователя', 'client_search')
    list = getButton('👨‍💻 Список клиентов', 'client_list', '', 1)
    main = kb_inl_admin.go_main_btn

    keyboard.add(ban, list)
    keyboard.add(search, main)
    return keyboard


def kb_admin_users_list(pages: int, page: int, filter: str = '', is_filter=True):
    def getListButton(text: str, new_page: int, new_filter=None):
        new_filter = new_filter if (new_filter is not None) else filter
        btn_type = 'client_list' if is_filter else 'ban_list'
        return getButton(text, btn_type, new_filter, new_page)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    btn_start = getListButton('В начало', 1)
    btn_end = getListButton('В конец', pages)
    btn_next = getListButton('Далее', page + 1)
    btn_back = getListButton('Назад', page - 1)

    counter = getButton(f'{page}/{pages}', 'counter')
    search = getButton('🔎 Поиск пользователя', 'client_search', filter, page)

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

    if is_filter:
        keyboard.add(btn_filter)

    keyboard.add(search)
    keyboard.add(kb_inl_admin.go_users_btn, kb_inl_admin.go_main_btn)

    return keyboard


def kb_admin_client_info(client_db_id: int, is_banned: bool, page=1, filter=''):
    def getClientButton(text: str, type: str):
        return getButton(text, type, '', 1, client_db_id)

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
    btn_add_trial_sub = getClientButton(
        'Выдать пробный доступ', 'client_set_trial_custom'
    )

    # if filter != '' or page != 1:
    #     btn_client_list = getButton(
    #         '👨‍💻 Список клиентов', 'client_list', filter, page
    #     )
    # else:
    #     btn_client_list = kb_inl_admin.go_users_btn
    btn_client_list = kb_inl_admin.go_users_btn

    keyboard.add(btn_add_sub, btn_remove_sub)
    keyboard.add(btn_add_trial_sub)
    keyboard.add(btn_ban, btn_client_list)
    return keyboard


def kb_admin_users_cancel(filter='', page=1):
    keyboard = InlineKeyboardMarkup(row_width=2)

    # if filter != '' or page != 1:
    #     btn_client_list = getButton(
    #         '👨‍💻 Список клиентов', 'client_list', filter, page
    #     )
    # else:
    #     btn_client_list = kb_inl_admin.go_users_btn
    btn_client_list = kb_inl_admin.go_users_btn

    keyboard.add(btn_client_list)
    return keyboard


def kb_admin_users_confirm(type_info: str, client_db_id: int):
    def getConfimButton(text: str, type: str):
        return getButton(text, f'confirm_{type}_{type_info}', '', 1, client_db_id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_yes = getConfimButton('Да', 'yes')
    btn_no = getConfimButton('Нет', 'no')

    keyboard.add(btn_yes, btn_no)
    return keyboard


def kb_admin_users_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(kb_inl_admin.go_users_btn, kb_inl_admin.go_main_btn)
    return keyboard
