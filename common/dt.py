import re
from typing import Literal
from datetime import datetime, timedelta, timezone


DT_PRINT_TYPE = Literal['date', 'time', 'datetime']


def get_datetime_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_str_by_datetime(dt: datetime, type: DT_PRINT_TYPE = 'datetime') -> str:
    """
        Возвращает строку даты и времени по типу вывода \n
        дата / время / дата и время
    """
    formats: dict[DT_PRINT_TYPE, str] = {
        'date': '%d.%m.%Y',
        'time': '%H:%M',
        'datetime': '%d.%m.%Y %H:%M',
    }

    return (dt + timedelta(hours=3)).strftime(formats[type])


def get_datetime_by_str(value: str):
    """
        Возвращает дату и время по строке, либо False, если не верный формат
        \nФормат:
        \n(Д[. ]М[. ]Г Ч[: ]М)
        \n(Д[. ]М[. ]Г)
        \n(Д[. ]М)
        \nД, М, Ч, М - день, месяц, часы, минуты 1 или 2 значные числа
        \nГ - год 4 или 2 значный (20xx)
    """
    datetime_pattern = r'^(0?[1-9]|[1-2]\d|3[0-1])[ .]+(0?[1-9]|1[0-2])(?:[ .]+(\d{4}|\d{2}))?(?:[ ]+([0-1]?\d|2[0-3])[: ]+([0-5]?\d))?$'

    reg = re.search(datetime_pattern, value)
    if reg is None:
        return False

    day = int(reg.group(1))
    month = int(reg.group(2))
    year = reg.group(3)
    if year is None:
        year = get_datetime_now().year
    elif len(year) == 2:
        year = int(f'20{year}')
    else:
        year = int(year)

    hour = int(reg.group(4) or '0')
    minute = int(reg.group(5) or '0')

    try:
        return datetime(year, month, day, hour, minute)
    except:
        return False
