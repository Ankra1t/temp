import json
from typing import Optional
from config_global import API_URL
from services.base_config import session_decorator, session, check_response


@session_decorator
def update(
    id: int, message: Optional[str], photo: Optional[str]
):
    if message is None and photo is None:
        return

    data = {}
    if message is not None:
        data['message'] = message
    if photo is not None:
        data['photo'] = message

    res = session.post(
        f'{API_URL}/violation/{id}',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def create(
    userId: int, status: bool
):
    data = {
        'userId': userId,
        'status': status,
    }

    res = session.post(
        f'{API_URL}/violation',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def getMonthPoints(
    userId: int
) -> int | None:
    res = session.get(
        f'{API_URL}/violation/monthPoints/{userId}',
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def getToday(
    userId: int
) -> int | None:
    res = session.get(
        f'{API_URL}/violation/today/{userId}',
    )

    if not check_response(res):
        return

    return res.json()
