from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt

from .filter import channel_post_factory


def getButton(text: str, type: str, page: int = 0, stat_id: int = 0):
    return InlineKeyboardButton(
        text, None,
        channel_post_factory.new(
            type=type, page=page, stat_id=stat_id
        )
    )


def kb_channel_post():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_results = getButton("Результаты", 'results')
    btn_channel_stats = getButton("Статистика", 'ch_stats')
    btn_send_settings = getButton("Настройки", 'send_settings')
    btn_menu = getButton("На главную", 'main')

    keyboard.add(btn_results)
    keyboard.add(btn_send_settings, btn_channel_stats)
    keyboard.add(btn_menu)
    return keyboard


def kb_channel_stat():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_channel_stats = getButton("Отправить", 'ch_stats_send')
    btn_cancel = getButton("Отмена", 'back')
    keyboard.add(btn_channel_stats, btn_cancel)
    return keyboard


def kb_send_settings(stop: bool, vote: bool):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_stop = getButton(
        "Включить стоп" if not stop else 'Выключить стоп', 'ss_stop')
    btn_vote = getButton(
        "Включить опрос" if not vote else 'Выключить опрос', 'ss_vote')
    btn_style = getButton("Изменить стиль", 'ss_style')
    btn_time = getButton("Изменить период", 'ss_time')
    btn_back = getButton(back_txt('ru'), 'back')

    keyboard.add(
        btn_stop, btn_vote,
        btn_style, btn_time,
        btn_back
    )
    return keyboard


def kb_send_settings_calc_time():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton('Среднесрочная', f'ss_time=avg'),
        getButton('Внутридневная', f'ss_time=day'),
        getButton('Убрать', f'ss_time=none'),
    )
    return keyboard


def kb_send_settings_trading_style():
    def getThisButton(text: str, style: str):
        return getButton(
            text, f'ss_style={style}',
        )

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    styles = {
        'Пробой': 'пробой уровня',
        'Отбой': 'отбой от уровня',
        'Ложные': 'ложные пробои',
        'Скользящие': 'скользящие средние',
        'high/low': 'торговля на high/low',
    }

    buttons = []
    for key in styles.keys():
        buttons.append(getThisButton(key, styles[key]))
        if len(buttons) == row_width:
            keyboard.add(*buttons)
            buttons = []

    btn_off = getThisButton('⭕️ Выключить', '**off**')

    buttons.append(btn_off)
    if len(buttons) != 0:
        keyboard.add(*buttons)

    keyboard.add(getButton(back_txt('ru'), 'send_settings'))
    return keyboard


def kb_channel_calc_result(
    current_page: int,
    page_count: int,
    stat_id: int,
    in_deal: bool,
):
    keyboard = InlineKeyboardMarkup(row_width=3)

    if page_count > 1:
        if current_page == 0:
            btn_prev = getButton('В конец', 'results', page_count - 1)
        else:
            btn_prev = getButton('Назад', 'results', current_page - 1)

        if current_page == page_count - 1:
            btn_next = getButton('В начало', 'results', 0)
        else:
            btn_next = getButton('Вперед', 'results', current_page + 1)

        btn_counter = getButton(f'{current_page + 1}/{page_count}', 'counter++')

        keyboard.add(btn_prev, btn_counter, btn_next)

    if in_deal:
        btn_tp = getButton('Тейк', 'result_take', current_page, stat_id)
        btn_sl = getButton('Стоп', 'result_stop', current_page, stat_id)
        keyboard.add(btn_tp, btn_sl)
    else:
        btn_deal = getButton('В сделке', 'result_deal', current_page, stat_id)
        btn_cancel = getButton(
            'Отмена сделки', 'result_cancel', current_page, stat_id
        )
        keyboard.add(btn_cancel, btn_deal)

    keyboard.add(
        getButton(
            back_txt('ru'), 'back',
            current_page, stat_id
        )
    )

    return keyboard


def kb_channel_calc_result_take(tp_values: list[int], stat_id: int, page: int):
    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []
    for i, el in enumerate(tp_values):
        btn = getButton(f'x{el}', f'take+{el}', page, stat_id)
        buttons.append(btn)
        if len(buttons) == row_width or (i == len(tp_values) - 1 and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    keyboard.add(
        getButton(back_txt('ru'), 'results' if page != -1 else 'calc', page, stat_id)
    )

    return keyboard


def kb_channel_calc_result_stop(stat_id: int, page: int):
    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    sl_count = [1, 1.5, 2]

    buttons = []
    for i, el in enumerate(sl_count):
        btn = getButton(f'x{el}', f'stop+{el}', page, stat_id)
        buttons.append(btn)
        if len(buttons) == row_width or (i == len(sl_count) - 1 and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    keyboard.add(
        getButton(back_txt('ru'), 'results' if page != -1 else 'calc', page, stat_id)
    )

    return keyboard


def kb_channel_post_back():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(back_txt('ru'), 'back')
    )
    return keyboard
