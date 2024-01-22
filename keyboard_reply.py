from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from initialize import kb_inl_admin

# ===================== REDACTOR


def kb_main_redactor():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn3 = InlineKeyboardButton(
        "Постинг", callback_data='adm_posting')
    btn6 = InlineKeyboardButton(
        "Главная", callback_data='redactor_main')
    keyboard.add(btn3, btn6)
    return keyboard


# ==================== SUPPORT
def kb_main_support():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(
        "Список заявок", callback_data='application_list'
    )
    keyboard.add(btn1)
    return keyboard


# Подтверждение отправки быстрого поста
def kb_admin_livepost_request():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(
        text="Live", callback_data="live_send_now")
    button2 = InlineKeyboardButton(
        text="Точнее", callback_data="live_signal")
    button3 = InlineKeyboardButton(
        text="Отмена", callback_data="live_cancel")
    keyboard.add(button1, button2)
    keyboard.add(button3)
    return keyboard


def kb_live_cancel():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button3 = InlineKeyboardButton(
        text="Отмена", callback_data="live_cancel")
    keyboard.add(button3)
    return keyboard


# ====================== USERS
def kb_user_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_yes = InlineKeyboardButton(
        text="О нас", callback_data="user_about_us")
    btn_no = InlineKeyboardButton(text="FAQ", callback_data="user_faq")
    btn_no3 = InlineKeyboardButton(
        text="Тех.поддержка", callback_data="user_sup")

    keyboard.add(btn_yes, btn_no, btn_no3)
    return keyboard


def kb_user_go_back():
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_back = InlineKeyboardButton(
        text="Назад⬅️", callback_data="user_go_back")
    keyboard.add(btn_back)
    return keyboard


def kb_user_sup(link: str):
    link = link.replace('@', '')
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn = InlineKeyboardButton(
        "Перейти к оператору", f'https://t.me/{link}'
    )

    keyboard.add(btn, kb_inl_admin.go_main_btn)

    return keyboard


# ========= Кальклуятор
def kb_users_bill(price, pay_link):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn = InlineKeyboardButton(
        text=f"Оплатить {price} через CryptoBot", url=pay_link)
    keyboard.add(btn)
    return keyboard


# ======================= // ANCHOR ССЫЛКА НА БОТА С СИГНАЛАМИ
def kb_link_main_bot():
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton(
        text="Сигналы", url="https://t.me/ForPeoplePrivate_bot")
    keyboard.add(btn)
    return keyboard
