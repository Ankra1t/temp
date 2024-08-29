from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter

from common.keyboard import back_txt


admin_posts_factory = CallbackData('type', prefix='admin_posts')


class AdminPostsCallbackFilter(AdvancedCustomFilter):
    key = 'admin_posts'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str):
    return InlineKeyboardButton(text, None, admin_posts_factory.new(type=type))


def kb_posts():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('📝 Добавить пост', 'add')
    btn2 = getButton('❌ Удалить пост', 'delete')
    btn3 = getButton('🔎 Все посты', 'list')
    btn4 = getButton('✉️ Отправить сейчас', 'send_now')

    back = getButton(back_txt(), 'go_main')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    keyboard.add(btn4, back)
    return keyboard


def kb_post_kinds():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton('ℹ️ Информационный', 'choose_kind_post')
    btn2 = getButton('📈 Рекомендация', 'choose_kind_signal')

    keyboard.add(btn1, btn2)
    back = getButton(back_txt(), 'go_posts')

    keyboard.add(back)
    return keyboard


def kb_posts_back():
    keyboard = InlineKeyboardMarkup(row_width=2)
    back = getButton(back_txt(), 'go_posts')
    keyboard.add(back)
    return keyboard


def kb_post_add_confirm():
    keyboard = InlineKeyboardMarkup(row_width=2)

    prefix = 'add_'
    btn1 = getButton('💵 Платным', prefix + 'private')
    btn2 = getButton('👨‍💻 Всем', prefix + 'all')
    btn3 = getButton('Бесплатным', prefix + 'public')

    back = getButton(back_txt(), 'go_posts')

    keyboard.add(btn1, btn2)
    # keyboard.add(btn3)
    keyboard.add(back)
    return keyboard


def kb_post_confirm(type: str):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_yes = getButton('✅ Да', type + '_confirm_yes')
    btn_no = getButton('❌ Нет', type + '_confirm_no')

    keyboard.add(btn_yes, btn_no)
    return keyboard
