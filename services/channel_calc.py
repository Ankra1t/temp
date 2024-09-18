import json

from pydantic.type_adapter import TypeAdapter

from config_global import API_URL
from .base_config import session_decorator, session, check_response
from models import Live, MonthToolStats, SendCalc, CalcSentMessages, SentMessages, LANGUAGES_TYPE


@session_decorator
def get(id: int):
    res = session.get(f'{API_URL}/channelCalc/{id}')

    if not check_response(res):
        return

    return SendCalc.model_validate_json(res.text)


@session_decorator
def getByCalc(id: int):
    res = session.get(f'{API_URL}/channelCalc/calcId/{id}')

    if not check_response(res):
        return

    return SendCalc.model_validate_json(res.text)


@session_decorator
def getSentMessagesByCalc(calcId: int):
    res = session.get(f'{API_URL}/channelCalc/calcId/{calcId}/messages')

    if not check_response(res):
        return

    data = res.json()
    if data is None:
        return
    return CalcSentMessages(**data)


@session_decorator
def getSentToday():
    res = session.get(f'{API_URL}/channelCalc/sentToday')

    if not check_response(res):
        return

    return TypeAdapter(list[SendCalc]).validate_json(res.text)


@session_decorator
def getInWait():
    res = session.get(f'{API_URL}/channelCalc/inWait')

    if not check_response(res):
        return

    return TypeAdapter(list[SendCalc]).validate_json(res.text)


@session_decorator
def getSent():
    res = session.get(f'{API_URL}/channelCalc/sent')

    if not check_response(res):
        return

    return TypeAdapter(list[SendCalc]).validate_json(res.text)


@session_decorator
def create(calcId: int):
    data = {'calcId': calcId}

    res = session.post(
        f'{API_URL}/channelCalc',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return SendCalc.model_validate_json(res.text)


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

    return SendCalc.model_validate_json(res.text)


@session_decorator
def createWeekStat(channels: list[int], messages: list[int], langs: list[LANGUAGES_TYPE]):
    data = {
        'channels': [str(el) for el in channels],
        'messages': [str(el) for el in messages],
        'langs': langs,
    }

    res = session.post(
        f'{API_URL}/channelCalc/weekStat',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def getWeekStat(calcId: int | None = None):
    data = None
    if calcId:
        data = {
            'calcId': calcId
        }

    res = session.get(
        f'{API_URL}/channelCalc/weekStat',
        params=data
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def getLiveInfo():
    res = session.get(
        f'{API_URL}/channelCalc/live-info',
    )

    if not check_response(res):
        return

    return Live.model_validate_json(res.text)


@session_decorator
def updateLiveInfo(data: SentMessages):
    res = session.post(
        f'{API_URL}/channelCalc/live-info',
        data.model_dump_json().encode()
    )

    if not check_response(res):
        return

    return True

@session_decorator
def getMonthToolCount(tool: str):
    res = session.get(
        f'{API_URL}/channelCalc/monthCount/{tool.replace("/", "")}',
    )

    if not check_response(res):
        return

    return MonthToolStats.model_validate_json(res.text)
