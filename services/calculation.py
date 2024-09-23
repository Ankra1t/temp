import json
from typing import Literal
from config_global import API_URL
from models import Calculation, ForexInfo
from services.base_config import check_response, session_decorator, session


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
    id: int, minutes: int
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
def updateTrailingStop(
    id: int, trailingStop: int
):
    res = session.post(
        f'{API_URL}/calculations/{id}/trailingStop',
        json.dumps({
            "trailingStop": trailingStop
        }).encode()
    )

    if not check_response(res):
        return

    return True


@session_decorator
def getTrailingStops(
    id: int
):
    res = session.get(
        f'{API_URL}/calculations/{id}/trailingStops',
    )

    if not check_response(res):
        return

    return True
