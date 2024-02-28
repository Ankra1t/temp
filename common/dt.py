from datetime import datetime, timedelta
from typing import Literal


DT_PRINT_TYPE = Literal['date', 'time', 'datetime']


def get_datetime_now():
    return datetime.utcnow()


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
