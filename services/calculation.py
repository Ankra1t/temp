from io import BufferedReader
import json
from typing import Literal, Optional, TypedDict
from typing_extensions import Unpack, NotRequired

from config_global import API_URL
from models import Calculation, ForexInfo
from services.base_config import check_response, session_decorator, session


class UpdateActiveCalc(TypedDict):
    autoStop: NotRequired[Optional[bool]]
    autoTake: NotRequired[Optional[float]]
    trailingStopCount: NotRequired[Optional[float]]
    chMesIds: NotRequired[Optional[str]]


@session_decorator
def getByUserList(*, userId: int, type: Literal['deal', 'wait', 'done', 'canceled']):
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
def get(*, userId: int, calcId: int):
    res = session.get(f'{API_URL}/calculations/{calcId}')
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
def getWeekStats(*, userId: int):
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
    *,
    userId: int,
    calcId: int,
    **kwargs
):
    res = session.post(
        f'{API_URL}/calculations/{calcId}',
        json.dumps(kwargs).encode()
    )

    if not check_response(res):
        return

    return Calculation(**res.json())


@session_decorator
def closeActive(
    *,
    userId: int,
    calcId: int,
):
    res = session.post(
        f'{API_URL}/calculations/{calcId}/closeActive',
    )

    if not check_response(res):
        return

    return Calculation(**res.json())


@session_decorator
def updateCancelAt(
    *, userId: int, id: int, minutes: int | None
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
    *, userId: int, id: int, **data: Unpack[UpdateActiveCalc]
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
    *, userId: int, id: int
):
    res = session.post(
        f'{API_URL}/calculations/{id}/activate',
    )

    if not check_response(res):
        return

    return True


@session_decorator
def finishActive(
    *, userId: int, id: int
):
    res = session.post(
        f'{API_URL}/calculations/{id}/finishActive',
    )

    if not check_response(res):
        return

    return Calculation.model_validate_json(res.text)


@session_decorator
def sendPhoto(
    *, userId: int, file: BufferedReader
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
