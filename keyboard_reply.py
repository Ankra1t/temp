from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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



