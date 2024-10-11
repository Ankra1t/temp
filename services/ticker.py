
import json
from typing import Optional
from models import TickerInfo
from services.base_config import check_response, session_decorator, session
from config_global import API_URL


@session_decorator
def get_info(ticker: str):
    res = session.get(
        f'{API_URL}/tg/getTicker/{ticker.replace("/", "").upper()}',
    )

    if not check_response(res):
        return

    return TickerInfo(**res.json())


@session_decorator
def get_atr(ticker: str, period: str, count: int):
    res = session.get(
        f'{API_URL}/tg/getAvgAtr/{ticker.replace("/", "").upper()}',
        params={
            'period': period,
            'count': count
        }
    )
    if not check_response(res):
        return

    return res.json()


@session_decorator
def get_delivery_fee(ticker: str):
    res = session.get(
        f'{API_URL}/tg/{ticker.replace("/", "").upper()}/deliveryFee',
    )
    if not check_response(res):
        return

    return float(res.json())


@session_decorator
def get_text(isSpot: Optional[bool] = None, turnover: Optional[float] = None) -> Optional[str]:
    data = {
        "isSpot": isSpot,
        "turnover": turnover
    }

    res = session.post(
        f'{API_URL}/tg/getTickers',
        json.dumps(data).encode()
    )
    if not check_response(res):
        return

    return res.text
