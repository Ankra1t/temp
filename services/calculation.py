import json
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
def getByUserInWait(userId: int):
    data = {
        'userId': userId
    }

    res = session.post(
        f'{API_URL}/calculations/inWait',
        json.dumps(data).encode()
    )
    if not check_response(res):
        return

    calculations = []
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
def getByUserFinish(userId: int):
    data = {
        'userId': userId
    }

    res = session.post(
        f'{API_URL}/calculations/finish',
        json.dumps(data).encode()
    )
    if not check_response(res):
        return

    calculations = []
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
