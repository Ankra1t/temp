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






