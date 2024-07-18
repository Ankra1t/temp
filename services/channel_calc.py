import json
from config_global import API_URL
from .base_config import session_decorator, session, check_response
from models import SendCalc


@session_decorator
def get(id: int):
    res = session.get(f'{API_URL}/channelCalc/{id}')

    if not check_response(res):
        return

    return SendCalc(**res.json())


@session_decorator
def getByCalc(id: int):
    res = session.get(f'{API_URL}/channelCalc/calcId/{id}')

    if not check_response(res):
        return

    return SendCalc(**res.json())


@session_decorator
def getSentToday():
    res = session.get(f'{API_URL}/channelCalc/sentToday')

    if not check_response(res):
        return

    return [SendCalc(**el) for el in res.json()]


@session_decorator
def getSent():
    res = session.get(f'{API_URL}/channelCalc/sent')

    if not check_response(res):
        return

    return [SendCalc(**el) for el in res.json()]


@session_decorator
def create(calcId: int):
    data = {'calcId': calcId}

    res = session.post(
        f'{API_URL}/channelCalc',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return SendCalc(**res.json())


@session_decorator
def update(
    id: int, **kwargs
):
    res = session.post(
        f'{API_URL}/channelCalc/{id}',
        json.dumps(kwargs).encode()
    )

    if not check_response(res):
        return

    return SendCalc(**res.json())


@session_decorator
def createWeekStat(channels: list[int], messages: list[int]):
    data = {
        'channels': [str(el) for el in channels],
        'messages': [str(el) for el in messages],
    }

    res = session.post(
        f'{API_URL}/channelCalc/weekStat',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def getWeekStat():
    res = session.get(
        f'{API_URL}/channelCalc/weekStat',
    )

    if not check_response(res):
        return

    return res.json()
