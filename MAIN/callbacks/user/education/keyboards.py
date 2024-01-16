from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .filter import user_education_factory


def getButton(text: str, type: str, page: int | None = None, num_les: int | None = None):
    return InlineKeyboardButton(
        text, None,
        user_education_factory.new(
            type=type, page=page or -1, num_les=num_les or -1)
    )


def kb_user_education():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = getButton("Терминология", 'terms')
    btn2 = getButton("Бесплатный курс", 'curs')
    btn3 = getButton("Назад", 'back')

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    return keyboard


def kb_user_pages(num_page: int, max_page: int):
    def getThisButton(text: str, type: str):
        return getButton(text, f'terms_{type}', num_page)

    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_prev = getThisButton('Назад', 'prev')
    btn_next = getThisButton('Вперед', 'next')
    btn_start = getThisButton('В начало', 'start')
    btn_end = getThisButton('В конец', 'end')
    counter = getThisButton(f'{num_page}/{max_page}', 'counter')
    back = getButton('Назад', 'go_education')

    if num_page == 1:
        keyboard.add(btn_end, counter, btn_next)
    elif num_page == max_page:
        keyboard.add(btn_prev, counter, btn_start)
    else:
        keyboard.add(btn_prev, counter, btn_next)

    keyboard.add(back)
    return keyboard


def kb_user_curs(count: int):
    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons_added = []

    for i in range(1, count + 1):
        buttons_added.append(getButton(f"{i} Урок", 'curs_les', 1, i))

        if len(buttons_added) == row_width:
            keyboard.add(*buttons_added)
            buttons_added = []

    if buttons_added:
        keyboard.add(*buttons_added)

    back = getButton('Назад', 'go_education')
    keyboard.add(back)
    return keyboard


def kb_user_lesson(num_page: int, max_page: int, num_les: int):
    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_all = getButton('Все уроки', 'curs')
    counter = getButton(f'{num_page}/{max_page}', 'curs_counter')

    btn_start = getButton('В начало', 'curs_les', 1, num_les)
    btn_prev = getButton('Назад', 'curs_les', num_page - 1, num_les)
    btn_next = getButton('Далее', 'curs_les', num_page + 1, num_les)
    btn_prev_les = getButton('Предыдущий урок', 'curs_les', 1, num_les - 1)
    btn_next_les = getButton('Следующий урок', 'curs_les', 1, num_les + 1)

    if num_page == 1:
        keyboard.add(btn_prev_les, counter, btn_next)
    elif num_page == max_page:
        keyboard.add(btn_prev, counter, btn_next_les)
    else:
        keyboard.add(btn_prev, counter, btn_next)

    keyboard.add(btn_all)
    return keyboard
