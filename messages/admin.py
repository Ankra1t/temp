from common.dt import get_datetime_now, get_str_by_datetime
from common.utils import get_print_float
from messages.common import POINT
from models import LANGUAGES_TYPE, Price


def msg_admin_main(
        count_all: int,
        count_with_sub: int,
        count_blocked: int,
        count_admins: int,
        count_today_users: int,
        count_first_tries: int,
        count_first_lang: int,
        count_refs: int,
        lang_counts: dict[LANGUAGES_TYPE, int]
):
    return f"""🏠 <b><u>Главная</u></b>

В базе: {count_all}
Заблокировали бота: {count_blocked}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}

Зарегестрировались сегодня: {count_today_users}
Из них выбрали язык: {count_first_lang}
    Русский: {lang_counts['ru']}
    Английский: {lang_counts['en']}
    Узбекский: {lang_counts['uz']}
    Турецкий: {lang_counts['tr']}
Из них провели тестовый расчёт: {count_first_tries}

Количество администраторов: {count_admins}
Количество по рефералке: {count_refs}"""


def msg_admin_users(count_all: int, count_with_sub: int, count_blocked: int, lang_counts:dict[LANGUAGES_TYPE, int]):
    return f"""👨 <b><u>Пользователи</u></b>

Всего: {count_all}

Заблокировали бота: {count_blocked}
Платных: {count_with_sub}
Бесплатных: {int(count_all) - int(count_with_sub)}

Русский: {lang_counts['ru']}
Английский: {lang_counts['en']}
Узбекский: {lang_counts['uz']}
Турецкий: {lang_counts['tr']}"""


def msg_admin_menu(title: str):
    return f"""<b><u>{title}</u></b>

Действия:"""


def msg_admin_fut_posts(posts_count: int):
    return f"""📋 <b><u>Отложенные посты</u></b>

Количество: <b>{posts_count}</b>"""


def msg_admin_tariff(tariff: Price):
    discount = ''
    if tariff.discount is not None:
        now = get_datetime_now()
        if tariff.discount.findate > now:
            fin_date = get_str_by_datetime(tariff.discount.findate)
            discount = f'Скидка <b>{get_print_float(tariff.discount.percent, 2)}%</b> до {fin_date}'

    return f"""
{tariff.name}
<b>{get_print_float(tariff.price)} {tariff.currency}</b>
{tariff.description}

Продукт: <b>{tariff.type_product}</b>
Действует <b>{tariff.duration_days}</b> дней
""" + (f'\n{discount}' if discount != '' else '')


def msg_admin_users_markets(counts: dict[str, int]):
    return f"""<b><u>Клиенты по рынкам</u></b>

{POINT} Крипта: <b>{counts.get('crypto', 0)}</b>
{POINT} Форекс: <b>{counts.get('forex', 0)}</b>
{POINT} РФ: <b>{counts.get('RF', 0)}</b>
{POINT} США: <b>{counts.get('USA', 0)}</b>"""


def msg_admin_send_settings(stop: bool, vote: bool, style: str | None, time: str | None):
    text_time = {
        'avg': 'Среднесрочная',
        'day': 'Внутридневная',
    }

    return f"""<u><b>Настройка отправки</b></u>

Отправка стопа: {'Да' if stop else 'Нет'}
Отправка опроса: {'Да' if vote else 'Нет'}
Базовый стиль: {style or '-'}
Базовый период: {text_time[time] if time is not None else '-'}"""
