from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.keyboard import back_txt

from .filter import admin_main_factory


def getButton(text: str, type: str):
    return InlineKeyboardButton(
        text, None,
        admin_main_factory.new(type=type)
    )


def kb_admin_main():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_users = getButton("Пользователи", 'users')
    btn_workers = getButton("Работники", 'workers')
    btn_posts = getButton("Отложенные посты", 'fut_posts')
    btn_payments = getButton("Оплата", 'payment')
    btn_params = getButton("Параметры", 'params')
    btn_tariffs = getButton("Тарифы", 'tariffs')
    btn_send_settings = getButton("Отправка сигналов", 'send_settings')
    btn_site_code = getButton("Войти на сайт", 'site_code')
    btn_channel_stats = getButton("Статистика в каналы", 'ch_stats')

    keyboard.add(btn_users, btn_workers)
    keyboard.add(btn_posts, btn_payments)
    keyboard.add(btn_params, btn_tariffs)
    keyboard.add(btn_send_settings)
    keyboard.add(btn_channel_stats)
    keyboard.add(btn_site_code)
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
