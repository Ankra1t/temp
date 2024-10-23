import json

from services.base_config import check_response, session_decorator, session
from models import SentMessages, UserNotification
from config_global import API_URL


@session_decorator
def registration(*, userId: int, username: str | None = None, referId: int | None = None):
    data = {
        'tgId': userId,
        'tgUsername': username,
        'referId': referId
    }

    res = session.post(
        f'{API_URL}/tg/auth/registration',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return True


@session_decorator
def addUserNotificationMessages(*, userId: int, value: SentMessages, lang: str, num: int):
    data = {
        'chIds': value.chIds,
        'mesIds': value.mesIds,
        'langs': value.langs,
        'firstLang': lang,
        'num': num,
    }

    res = session.post(
        f'{API_URL}/users/{userId}/notMessages',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return UserNotification(**res.json())


@session_decorator
def getUserNotificationMessages(*, userId: int):
    res = session.get(f'{API_URL}/users/{userId}/notMessages')

    if not check_response(res):
        return

    return UserNotification(**res.json())


@session_decorator
def change_password(*, userId: int, password: str):
    data = {
        'id_telegram': userId,
        'password': password,
    }

    res = session.post(
        f'{API_URL}/auth/tg_change_pass',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return True


@session_decorator
def get_site_code(*, userId: int):
    data: dict[str, str | int] = {
        'id': userId,
    }

    res = session.post(
        f'{API_URL}/tg/auth/site_code',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return res.json().get('code')
