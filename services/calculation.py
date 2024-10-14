from io import BufferedReader
import json
from typing import Literal, Optional, TypedDict
from typing_extensions import Unpack, NotRequired

from config_global import API_URL
from models import Calculation, ForexInfo, UserActiveStats
from services.base_config import check_response, session_decorator, session


class UpdateActiveCalc(TypedDict):
    autoStop: NotRequired[Optional[bool]]
    autoTake: NotRequired[Optional[float]]
    trailingStopCount: NotRequired[Optional[float]]
    chMesIds: NotRequired[Optional[str]]


@session_decorator
def getByUser(userId: int):
    data = {
        'userId': userId
    }

    res = session.get(
        f'{API_URL}/calculations', params=data
    )
    if not check_response(res):
        return

    return [Calculation(**el) for el in res.json()]


@session_decorator
def getByUserList(userId: int, type: Literal['deal', 'wait', 'done', 'canceled']):
    data = {
        'userId': userId
    }

    url = ''
    if type == 'deal':
        url = 'inDeal'
    elif type == 'wait':
        url = 'inWait'
    elif type == 'canceled':
        url = 'canceled'
    else:
        url = 'finish'

    res = session.post(
        f'{API_URL}/calculations/{url}',
        json.dumps(data).encode()
    )
    if not check_response(res):
        return

    calculations: list[Calculation] = []
    for data in res.json():
        forex = None
        pair = data.get('pair')
        cross_prices = data.get('crossPrices')
        pair_price = data.get('pairPrice')
        if (pair is not None) and (pair_price is not None) and (cross_prices is not None):
            pairs = str(pair).split('/')
            forex = ForexInfo(
                pair=(pairs[0], pairs[1]),
                price=pair_price,
                cross_prices=json.loads(cross_prices)
            )

        calculations.append(Calculation(**data, forexInfo=forex))

    return calculations


@session_decorator
def get(id: int):
    res = session.get(f'{API_URL}/calculations/{id}')
    if not check_response(res):
        return

    data = res.json()

    forex = None
    pair = data.get('pair')
    cross_prices = data.get('crossPrices')
    pair_price = data.get('pairPrice')
    if (pair is not None) and (pair_price is not None) and (cross_prices is not None):
        pairs = str(pair).split('/')
        forex = ForexInfo(
            pair=(pairs[0], pairs[1]),
            price=pair_price,
            cross_prices=json.loads(cross_prices)
        )

    return Calculation(**data, forexInfo=forex)


@session_decorator
def getWeekStats(userId: int):
    data = {
        'userId': userId
    }

    res = session.post(
        f'{API_URL}/calculations/week',
        json.dumps(data).encode()
    )
    if not check_response(res):
        return

    return res.json()


@session_decorator
def update(
    id: int, **kwargs
):
    res = session.post(
        f'{API_URL}/calculations/{id}',
        json.dumps(kwargs).encode()
    )

    if not check_response(res):
        return

    return Calculation(**res.json())


@session_decorator
def updateCancelAt(
    id: int, minutes: int | None
):
    res = session.post(
        f'{API_URL}/calculations/{id}/cancelAt',
        json.dumps({
            "minutes": minutes
        }).encode()
    )

    if not check_response(res):
        return

    return Calculation(**res.json())


@session_decorator
def updateActive(
    id: int, **data: Unpack[UpdateActiveCalc]
):
    res = session.post(
        f'{API_URL}/calculations/{id}/updateActive',
        json.dumps(data).encode()
    )

    if not check_response(res):
        return

    return True


@session_decorator
def activate(
    id: int
):
    res = session.post(
        f'{API_URL}/calculations/{id}/activate',
    )

    if not check_response(res):
        return

    return True


@session_decorator
def finishActive(
    id: int
):
    res = session.post(
        f'{API_URL}/calculations/{id}/finishActive',
    )

    if not check_response(res):
        return

    return Calculation.model_validate_json(res.text)


@session_decorator
def getActiveStatsByUser(
    id: int
):
    res = session.get(
        f'{API_URL}/calculations/userActiveStats/{id}',
    )

    if not check_response(res):
        return

    return UserActiveStats.model_validate_json(res.text)


@session_decorator
def getActiveCalcsByUser(
    id: int, finished=False
):
    res = session.get(
        f'{API_URL}/calculations/activeByUser/{id}?finished={"true" if finished else "false"}',
    )

    if not check_response(res):
        return

    return UserActiveStats.model_validate_json(res.text)


@session_decorator
def sendPhoto(
    file: BufferedReader
):
    res = session.post(
        f'{API_URL}/calculations/photo',
        files={'file': file},
        headers={
            'content-type': None
        }
    )

    if not check_response(res):
        return

    return True
