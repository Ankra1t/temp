from common.utils import get_print_float
from models import LANGUAGES_TYPE, SubscribeInfo


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


def msg_admin_users(count_all: int, count_with_sub: int, count_blocked: int, lang_counts: dict[LANGUAGES_TYPE, int]):
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


def msg_admin_send_settings(
    stop: bool,
    vote: bool,
    style: str | None,
    time: str | None,
    trailingStop: float | None,
    cancelMinutes: float | None
):
    text_time = {
        'avg': 'Среднесрочная',
        'day': 'Внутридневная',
    }

    return f"""<u><b>Настройка отправки</b></u>

Отправка стопа: {'Да' if stop else 'Нет'}
Отправка опроса: {'Да' if vote else 'Нет'}
Базовый стиль: {style or '-'}
Базовый период: {text_time[time] if time is not None else '-'}

Скользящий стоп: {get_print_float(trailingStop, 1) if trailingStop else '-'}
Отмена через: {f'{get_print_float(cancelMinutes / 60, 1)} ч' if cancelMinutes else '-'}"""


def msg_admin_subs_list(data: list[SubscribeInfo]):
    data_show = ''

    if len(data) > 0:
        data_show = '\n'
        for el in data:
            name = f'@{el.user.tgUsername}' if el.user.tgUsername else f'id={el.user.tgId}'
            data_show += f'\n{el.id}. '
            data_show += '"Активация расчёта"' if el.productType == 'active_calc' else 'Кальулятор'
            data_show += f' ({name})'

    return f"""<b><u>Список подписок</u></b>{data_show}"""
