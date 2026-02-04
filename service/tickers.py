"""
Сервис тикеров для API tickers endpoints.

Этот модуль предоставляет методы для получения данных о тикерах,
включая информацию о ATR (Average True Range) и другие параметры.
Использует публичный API без аутентификации.
"""

import logging
from typing import Any, List, Optional

from config_global import API_AUTH_URL
from service.base import BaseData
from service.base_api import PublicApiClient, BaseApiError

logger = logging.getLogger(__name__)


# Модели данных для ответов API


class MetaPage(BaseData):
    """Метаинформация для ответа со списком тикеров."""

    page: int
    count: int
    total: int
    skip: Optional[int] = None


class LevelItem(BaseData):
    """Элемент уровня тикера."""

    id: int
    levelPrice: Optional[float] = None
    distancePct: Optional[float] = None
    placedSide: Optional[int] = None
    broken: bool
    isActive: bool
    inBand: bool


class TickerRawItem(BaseData):
    """
    Сырые данные тикера с расчётными ATR-полями.

    Содержит полную информацию о тикере, включая ATR, уровни,
    информацию о точности цены и количества.
    """

    atr: Optional[float] = None
    rangeAtrPct: Optional[float] = None
    absPeakAtrPct: Optional[float] = None
    atrPeriodUsed: Optional[int] = None
    levelsMinDistancePct: Optional[float] = None
    levels: List[LevelItem] = []
    priceTickSize: Optional[str] = None
    qtyStepSize: Optional[str] = None
    minQty: Optional[str] = None
    pricePrecision: Optional[int] = None
    qtyPrecision: Optional[int] = None
    marketType: Optional[str] = None
    # Основные поля
    sid: Optional[str] = None
    exchange: Optional[str] = None
    symbol: Optional[str] = None
    # Ценовые данные
    markPrice: Optional[float] = None
    indexPrice: Optional[float] = None
    percent24h: Optional[float] = None
    # Дополнительные поля
    turnover: Optional[float] = None
    fundingRate: Optional[float] = None
    high24h: Optional[float] = None
    low24h: Optional[float] = None
    volume24h: Optional[float] = None

    class Config:
        populate_by_name = True


class TickersRawResponse:
    """Ответ для endpoint со списком тикеров."""

    success: bool
    data: List[TickerRawItem]
    meta: MetaPage


class TickersApiError(BaseApiError):
    """Исключение для ошибок API тикеров."""

    pass


class TickersService(PublicApiClient[TickerRawItem]):
    """
    Сервис для операций с тикерами через публичный API.

    Использует PublicApiClient для выполнения HTTP запросов
    к endpoint /api/v2/tickers/raw без аутентификации.
    """

    def __init__(self, base_url: str = API_AUTH_URL) -> None:
        """
        Инициализировать сервис тикеров.

        Args:
            base_url: Базовый URL API (по умолчанию из конфигурации)
        """
        super().__init__(base_url)

    async def get_ticker_by_symbol(
        self,
        symbol: str,
        atr_period: int = 1,
        **kwargs: Any,
    ) -> Optional[TickerRawItem]:
        """
        Получить тикер по symbol с расчётом ATR.

        Args:
            symbol: Название монеты (например, "BTC" или "BTC/USDT")
                    Автоматически очищается от "/" и "USDT"/"usdt"
            atr_period: Период для расчёта ATR (по умолчанию 1)
            **kwargs: Дополнительные параметры запроса

        Returns:
            TickerRawItem с данными тикера или None

        Note:
            Возвращает первый тикер из отсортированного по turnover: desc списка.
            Это позволяет получить тикер с наибольшим оборотом.
        """
        try:
            # Очищаем symbol от "/" и окончаний "USDT"/"usdt"
            clean_symbol = symbol.replace(
                '/', ''
            ).replace('USDT', '').replace('usdt', '')

            if not clean_symbol:
                logger.warning("Empty symbol after cleaning")
                return None

            # Формируем параметры запроса (используем camelCase)
            params = {
                "symbol": clean_symbol,
                "atrPeriod": atr_period,
                **kwargs
            }
            query_string = "&".join(
                f"{k}={v}" for k, v in params.items() if v is not None)

            logger.debug(f"Fetching ticker with params: {query_string}")

            data = await self._request("GET", f"/tickers/raw?{query_string}")

            if not data.get("success") or not data.get("data"):
                logger.warning(f"No ticker found for symbol: {clean_symbol}")
                return None

            # Сортируем по turnover (убывание) и берем первый
            tickers = [TickerRawItem(**t) for t in data["data"]]
            sorted_tickers = sorted(
                tickers,
                key=lambda x: getattr(x, 'turnover', 0) or 0,
                reverse=True
            )

            result = sorted_tickers[0] if sorted_tickers else None
            if result:
                logger.debug(
                    f"Found ticker: {result.symbol} ({result.exchange}), "
                    f"ATR: {result.atr}, turnover: {result.turnover}"
                )
            return result

        except (BaseApiError, Exception) as e:
            logger.error(f"Error fetching ticker {symbol}: {e}")
            return None

    async def get_ticker_atr(
        self,
        symbol: str,
        atr_period: int = 1,
    ) -> Optional[float]:
        """
        Получить ATR для тикера по symbol.

        Args:
            symbol: Название монеты (например, "BTC" или "BTC/USDT")
            atr_period: Период для расчёта ATR

        Returns:
            Значение ATR или None, если не найдено
        """
        ticker = await self.get_ticker_by_symbol(symbol, atr_period=atr_period)
        return ticker.atr if ticker else None

    async def get_tickers_list(
        self,
        page: int = 1,
        count: int = 30,
        **kwargs: Any,
    ) -> Optional[List[TickerRawItem]]:
        """
        Получить список тикеров с пагинацией.

        Args:
            page: Номер страницы
            count: Количество элементов на странице
            **kwargs: Дополнительные фильтры

        Returns:
            Список тикеров или None
        """
        try:
            params = {
                "page": page,
                "count": count,
                **kwargs
            }
            query_string = "&".join(
                f"{k}={v}" for k, v in params.items() if v is not None)

            data = await self._request("GET", f"/tickers/raw?{query_string}")

            if not data.get("success") or not data.get("data"):
                return None

            return [TickerRawItem(**t) for t in data["data"]]

        except (BaseApiError, Exception) as e:
            logger.error(f"Error fetching tickers list: {e}")
            return None


# Глобальный экземпляр сервиса тикеров
tickers_service = TickersService()
