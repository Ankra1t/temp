import json

from pydantic.type_adapter import TypeAdapter

from config_global import API_URL
from .base_config import session_decorator, session, check_response
from models import SendCalc, SendCalcWithCalc


@session_decorator
def getByCalc(id: int):
    res = session.get(f'{API_URL}/channelCalc/calcId/{id}')

    if not check_response(res):
        return

    return SendCalc.model_validate_json(res.text)


@session_decorator
def getInWait():
    res = session.get(f'{API_URL}/channelCalc/inWait')

    if not check_response(res):
        return

    return TypeAdapter(list[SendCalcWithCalc]).validate_json(res.text)


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
