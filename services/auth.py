import json
from config_global import API_URL
from models import SentMessages
from services.base_config import check_response, session_decorator, session


@session_decorator
def registration(userId: int, username: str | None = None, referId: int | None = None):
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
def addUserNotificationMessages(userId: int, value: SentMessages):
    data = {
        'chIds': value.chIds,
        'mesIds': value.mesIds,
        'langs': value.langs,
    }

    res = session.post(
        f'{API_URL}/users/{userId}/notMessages',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return SentMessages(**res.json())


@session_decorator
def getUserNotificationMessages(userId: int):
    res = session.get(f'{API_URL}/users/{userId}/notMessages')

    if not check_response(res):
        return

    return SentMessages(**res.json())
