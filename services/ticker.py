
import json
from typing import Optional
from models import TickerInfo
from services.base_config import check_response, session_decorator, session
from config_global import API_URL, NEW_API_URL


@session_decorator
def get_info(ticker: str, exchange: str | None = None, type: str | None = None):
    spot = 'spot-' if type == 'spot' else ''

    # return {
    #   exchange:
    #     ticker.exchange.toLowerCase() === 'binance'
    #       ? ExchangeEnum.BINANCE
    #       : ExchangeEnum.BYBIT,
    #   indexPrice: ticker.price,
    #   type: type,
    #   name: ticker.symbol,
    #   percent24h: ticker.percent,
    #   turnover24h: ticker.turnover,
    #   createdAt: new Date(ticker.updated).toISOString(),
    # };

    res = session.get(
        f'{NEW_API_URL}//${spot}tickers/${(exchange or "bybit").lower()}-recent?symbol=${ticker.replace("/", "")}',
    )

    if not check_response(res):
        return

    result = res.json()

    if len(result) == 0:
        return

    tickerData = result[0]

    return TickerInfo(
        indexPrice=tickerData.price,
        percent24h=tickerData.percent,
        turnover24h=tickerData.turnover,
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
