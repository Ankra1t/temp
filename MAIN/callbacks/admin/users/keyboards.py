from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import admin_users_factory

from .handler import kb_inl_admin


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, admin_users_factory.new(type=type))


def kb_admin_users():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('Выдать подписку', 'put_subscribe')
    btn2 = getButton('Отменить подписку', 'cancel_subscribe')
    btn3 = getButton('Добавить/убавить', 'add_sub_subscribe')
    btn4 = getButton('Бан ⛔️', 'ban_list')
    btn5 = getButton('👨‍💻 Список клиентов   ','client_list+1')
    btn6 = kb_inl_admin.go_main_btn

    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5, btn6)
    return keyboard


def kb_admin_users_list(pages: int, page: int):
    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_start = getButton('В начало', 'client_list+1')
    btn_end = getButton('В конец', f'client_list+{pages}')
    btn_next = getButton('Далее', f'client_list+{page+1}')
    btn_back = getButton('Назад', f'client_list+{page-1}')
    counter = getButton(f'{page}/{pages}', 'counter')

    if page == 1:
        keyboard.add(btn_end, counter, btn_next)
    elif page == pages:
        keyboard.add(btn_back, counter, btn_start)
    else:
        keyboard.add(btn_back, counter, btn_next)

    keyboard.add(kb_inl_admin.go_users_btn, kb_inl_admin.go_main_btn)

    return keyboard


def kb_admin_users_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(kb_inl_admin.go_users_btn, kb_inl_admin.go_main_btn)
    return keyboard
