
import json
from typing import Optional
from models import TickerInfo
from services.base_config import check_response, session_decorator, session
from config_global import API_URL, NEW_API_URL


@session_decorator
def get_info(ticker: str, exchange: str | None = None, type: str | None = None):
    spot = 'spot-' if type == 'spot' else ''

    res = session.get(
        f'{NEW_API_URL}/{spot}tickers/{(exchange or "bybit").lower()}-recent?symbol={ticker.replace("/", "")}',
    )

    if not check_response(res):
        return

    result = res.json()
    tickers = result.get('response')

    if len(tickers) == 0:
        return

    tickerData = tickers[0]

    return TickerInfo(
        indexPrice=tickerData.get('price'),
        percent24h=tickerData.get('percent'),
        turnover24h=tickerData.get('turnover'),
        updatedAt=''
    )


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
