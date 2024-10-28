from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt, not_specify_txt

from models import STYLES, CallbackQuery


channel_post_factory = CallbackData(
    'type', 'stat_id', 'is_calc', 'page', prefix='channel_post'
)


class ChannelPostCallbackFilter(AdvancedCustomFilter):
    key = 'channel_post'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str, stat_id: int = 0, is_calc=False, page=0):
    return InlineKeyboardButton(
        text, None,
        channel_post_factory.new(
            type=type, stat_id=stat_id, is_calc=1 if is_calc else 0, page=page
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
    btn_trailing_stop = getButton("Скользящий стоп", 'ss_tr_stop')
    btn_cancel_at = getButton("Отмена через", 'ss_cancel_min')
    btn_back = getButton(back_txt('ru'), 'admin_main')

    keyboard.add(
        btn_stop, btn_vote,
        btn_style, btn_time,
        btn_trailing_stop, btn_cancel_at,
    )
    keyboard.add(btn_back)
    return keyboard


def kb_send_settings_trailing_stop():
    keyboard = InlineKeyboardMarkup(row_width=4)

    buttons = []
    for i in range(1, 5):
        buttons.append(
            getButton(f'{i}', f'ss_tr_stop+{i}')
        )

    keyboard.add(*buttons)
    keyboard.add(
        getButton(not_specify_txt('ru'), 'ss_tr_stop+0'),
        getButton(back_txt('ru'), 'send_settings')
    )
    return keyboard


def kb_send_settings_cancel_hours():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton('1h', 'ss_cancel_min+1h'),
        getButton('4h', 'ss_cancel_min+4h'),
        getButton('1d', 'ss_cancel_min+1d'),
    )
    keyboard.add(
        getButton(not_specify_txt(), 'ss_cancel_min+0'),
        getButton(back_txt(), 'send_settings'),
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

    buttons = []
    for key in STYLES.keys():
        buttons.append(getThisButton(key, STYLES[key]))
        if len(buttons) == row_width:
            keyboard.add(*buttons)
            buttons = []

    if len(buttons) != 0:
        keyboard.add(*buttons)

    keyboard.add(
        getThisButton('⭕️ Выключить', '**off**'),
        getButton(back_txt('ru'), 'send_settings')
    )
    return keyboard


def kb_channel_calc(
    calc_id: int,
    in_deal: bool,
    withoutStop: bool,
    is_calc=False,
    is_user=False,
):
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_take = getButton('Тейк', 'auto_take', calc_id)

    if not in_deal:
        keyboard.add(
            getButton('В сделке', 'result_deal', calc_id, is_calc),
            btn_take
        )
    else:
        keyboard.add(
            getButton('В ожидание', 'result_wait', stat_id=calc_id),
            btn_take
        )

    keyboard.add(
        getButton('Сдвинуть стоп', 'new_stop', calc_id, is_calc),
        getButton('Скользящий стоп', 'trailing_stop', calc_id, is_calc)
    )

    if not in_deal:
        keyboard.add(
            getButton(
                'Отмена сделки', 'result_cancel', calc_id, is_calc
            ),
            getButton('Время отмены', 'cancel_at', calc_id, is_calc),
        )

    keyboard.add(
        getButton('Комментарий', 'comment', calc_id),
        getButton(
            'Вывести стоп' if withoutStop else 'Не выводить стоп',
            'without_stop', calc_id
        )
    )

    keyboard.add(
        getButton('⚡️Завершение', 'result_result', calc_id),
        getButton(
            back_txt('ru'),
            'results' if not is_user else 'go_stats',
            calc_id, is_calc
        )
    )

    return keyboard


def kb_channel_calc_result(
    calc_id: int, in_deal: bool
):
    keyboard = InlineKeyboardMarkup(row_width=3)

    keyboard.add(
        getButton('Тейк', 'result_take', calc_id),
        getButton('Безубыток', 'take+0', calc_id),
        getButton('Стоп', 'result_stop', calc_id)
    )

    if in_deal:
        keyboard.add(
            getButton('Закрыть сделку', 'result_end', calc_id)
        )

    keyboard.add(
        getButton(
            back_txt('ru'), 'result', calc_id
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

    if is_calc:
        buttons.append(
            getButton(
                'Своя цена',
                'close_price', stat_id
            ),
        )

    buttons.append(
        getButton(
            back_txt('ru'),
            'calc' if is_calc else 'go_stats' if is_user else 'result_result', stat_id, is_calc
        )
    )

    keyboard.add(*buttons)
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

    if is_calc:
        buttons.append(
            getButton(
                'Своя цена',
                'close_price', stat_id
            ),
        )

    buttons.append(
        getButton(
            back_txt('ru'),
            'calc' if is_calc else 'go_stats' if is_user else 'result_result', stat_id, is_calc
        )
    )

    keyboard.add(*buttons)
    return keyboard


def kb_channel_post_list(page: int, pages_count: int):
    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []

    if pages_count > 1:
        if page == 0:
            buttons.append(getButton('-', 'counter'))
        else:
            buttons.append(getButton('<<', 'results', page=page - 1))

        buttons.append(
            getButton(f'{page + 1}/{pages_count}', 'counter')
        )

        if page == pages_count - 1:
            buttons.append(getButton('-', 'counter'))
        else:
            buttons.append(getButton('>>', 'results', page=page + 1))

    keyboard.add(*buttons)
    keyboard.add(
        getButton(back_txt('ru'), 'main')
    )
    return keyboard


def kb_channel_post_back():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(back_txt('ru'), 'main')
    )
    return keyboard


def kb_channel_post_back_to_result(calc_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(back_txt('ru'), 'result', calc_id)
    )
    return keyboard


def kb_trailing_stop(calc_id: int):
    keyboard = InlineKeyboardMarkup(row_width=4)

    buttons = []
    for i in range(1, 5):
        buttons.append(
            getButton(f'{i}', f'trailing+{i}', calc_id)
        )

    keyboard.add(*buttons)
    keyboard.add(
        getButton(back_txt('ru'), 'result', calc_id)
    )
    return keyboard


def kb_channel_cancel_at(calc_id: int):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton('1h', 'cancel_at+1h', calc_id),
        getButton('4h', 'cancel_at+4h', calc_id),
        getButton('1d', 'cancel_at+1d', calc_id),
    )
    keyboard.add(
        getButton(not_specify_txt(), 'cancel_at+0', calc_id),
        getButton(back_txt(), 'back_calc', calc_id),
    )
    return keyboard


def kb_result_end(calc_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton('❌ Нет', 'result_end_no', calc_id),
        getButton('✅ Да', 'result_end_yes', calc_id),
    )
    return keyboard
