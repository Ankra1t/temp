from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt

from .filter import channel_post_factory


def getButton(text: str, type: str, stat_id: int = 0, is_calc=False):
    return InlineKeyboardButton(
        text, None,
        channel_post_factory.new(
            type=type, stat_id=stat_id, is_calc=1 if is_calc else 0
        )
    )


def kb_channel_post():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_results = getButton("Результаты", 'results')
    btn_channel_stats = getButton("Статистика", 'ch_stats')
    btn_send_settings = getButton("Настройки отправки", 'send_settings')
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
        "Включить стоп" if not stop else 'Выключить стоп',
        'ss_stop'
    )
    btn_vote = getButton(
        "Включить опрос" if not vote else 'Выключить опрос',
        'ss_vote'
    )
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
    stat_id: int,
    in_deal: bool,
    is_calc=False,
    is_user=False,
):
    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_tp = getButton('Тейк', 'result_take', stat_id, is_calc)
    btn_sl = getButton('Стоп', 'result_stop', stat_id, is_calc)
    keyboard.add(btn_tp, btn_sl)

    if not in_deal:
        btn_deal = getButton('В сделке', 'result_deal', stat_id, is_calc)
        btn_cancel = getButton(
            'Отмена сделки', 'result_cancel', stat_id, is_calc
        )
        keyboard.add(btn_cancel, btn_deal)

    keyboard.add(
        getButton('Безубыток', 'take+0', stat_id, is_calc),
        getButton(
            back_txt('ru'), 'results' if not is_user else 'go_stats', stat_id, is_calc
        )
    )

    return keyboard


def kb_channel_calc_result_take(tp_values: list[int], stat_id: int, is_calc=False, is_user=False):
    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []
    for i, el in enumerate(tp_values):
        btn = getButton(f'x{el}', f'take+{el}', stat_id, is_calc)
        buttons.append(btn)
        if len(buttons) == row_width or (i == len(tp_values) - 1 and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    keyboard.add(
        getButton(
            back_txt('ru'),
            'calc' if is_calc else 'go_stats' if is_user else 'result', stat_id, is_calc
        )
    )

    return keyboard


def kb_channel_calc_result_stop(stat_id: int, is_calc=False, is_user=False):
    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    sl_count = [1, 1.5, 2]

    buttons = []
    for i, el in enumerate(sl_count):
        btn = getButton(f'x{el}', f'stop+{el}', stat_id, is_calc)
        buttons.append(btn)
        if len(buttons) == row_width or (i == len(sl_count) - 1 and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    keyboard.add(
        getButton(
            back_txt('ru'),
            'calc' if is_calc else 'go_stats' if is_user else 'result',
            stat_id, is_calc
        )
    )

    return keyboard


def kb_channel_post_back():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(back_txt('ru'), 'main')
    )
    return keyboard
