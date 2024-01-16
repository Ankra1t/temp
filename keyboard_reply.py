from telebot import types

# ===================== REDACTOR


def kb_main_redactor():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn3 = types.InlineKeyboardButton(
        "Постинг", callback_data='adm_posting')
    btn6 = types.InlineKeyboardButton(
        "Главная", callback_data='redactor_main')
    keyboard.add(btn3, btn6)
    return keyboard


# ==================== SUPPORT
def kb_main_support():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Список заявок")
    btn6 = types.KeyboardButton("Главная")
    keyboard.add(btn1, btn6)
    return keyboard


def kb_admin_users():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Выдать подписку")
    btn2 = types.KeyboardButton("Отменить подписку")
    btn3 = types.KeyboardButton("Добавить/убавить")
    btn4 = types.KeyboardButton("Список клиентов")
    btn5 = types.KeyboardButton("Главная")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    return keyboard


# Подтверждение отправки быстрого поста
def kb_admin_livepost_request():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(
        text="Live", callback_data="live_send_now")
    button2 = types.InlineKeyboardButton(
        text="Точнее", callback_data="live_signal")
    button3 = types.InlineKeyboardButton(
        text="Отмена", callback_data="live_cancel")
    keyboard.add(button1, button2)
    keyboard.add(button3)
    return keyboard


# ============== Постинг
def kb_admin_posting():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton("Платн: Новые посты")
    btn2 = types.KeyboardButton("Отложенные посты")
    # btn3 = types.KeyboardButton("Всем: Сделать рассылку")
    btn4 = types.KeyboardButton("Главная")
    # keyboard.add(btn1)
    keyboard.add(btn2)
    # keyboard.add(btn3)
    keyboard.add(btn4)
    return keyboard


# Отмена постинга
def kb_admin_posting_cancel():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отмена")
    keyboard.add(btn1)
    return keyboard

# ====================== USERS


def kb_user_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_yes = types.InlineKeyboardButton(
        text="О нас", callback_data="user_about_us")
    btn_no = types.InlineKeyboardButton(text="FAQ", callback_data="user_faq")
    btn_no3 = types.InlineKeyboardButton(
        text="Тех.поддержка", callback_data="user_sup")

    keyboard.add(btn_yes, btn_no, btn_no3)
    return keyboard


def kb_user_go_back():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_back = types.InlineKeyboardButton(
        text="Назад⬅️", callback_data="user_go_back")
    keyboard.add(btn_back)
    return keyboard


def kb_user_sup(link):
    link = link.replace('@', '')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    admin_users_del_yes1 = types.InlineKeyboardButton(
        text="Перейти к оператору", url=f'https://t.me/{link}')

    keyboard.add(admin_users_del_yes1)
    return keyboard


# ========= Кальклуятор
def kb_users_bill(price, pay_link):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn = types.InlineKeyboardButton(
        text=f"Оплатить {price} через CryptoBot", url=pay_link)
    keyboard.add(btn)
    return keyboard


# ======================= // ANCHOR ССЫЛКА НА БОТА С СИГНАЛАМИ
def kb_link_main_bot():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(
        text="Сигналы", url="https://t.me/ForPeoplePrivate_bot")
    keyboard.add(btn)
    return keyboard
