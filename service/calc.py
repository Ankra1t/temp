"""
Сервис расчётов для API calc endpoints.

Этот модуль предоставляет методы для операций расчётов, включая
получение списка расчётов и создание новых расчётов.
"""

import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

from config_global import API_AUTH_URL
from service.base import BaseData
from service.base_api import BaseApiClient, BaseApiError
from models import Calculation as ModelCalculation

logger = logging.getLogger(__name__)


# Модели ответов для API расчётов


class DealPrice(BaseData):
    """Информация о цене сделки."""

    min_price: float | None = Field(None, alias="minPrice")
    min_price_dt: int | None = Field(None, alias="minPriceDt")
    max_price: float | None = Field(None, alias="maxPrice")
    max_price_dt: int | None = Field(None, alias="maxPriceDt")

    class Config:
        populate_by_name = True


class TrailingStopItem(BaseData):
    """Значение трейлинг-стопа."""

    value: float | None = Field(None, alias="value")
    ts_created: int | None = Field(None, alias="ts_created")


class SplitFees(BaseData):
    """Распределение комиссий при разделении."""

    open_alloc: str | None = Field(None, alias="open_alloc")
    funding_alloc: str | None = Field(None, alias="funding_alloc")
    settle_alloc: str | None = Field(None, alias="settle_alloc")
    total: str | None = None


class SplitValue(BaseData):
    """Значение разделения (take profit)."""

    id: str
    price: str
    planned_qty: str = Field(..., alias="planned_qty")
    filled_qty: str = Field(..., alias="filled_qty")
    status: str
    created_at: int = Field(..., alias="created_at")
    updated_at: int = Field(..., alias="updated_at")
    fees: SplitFees
    take_count: str = Field(..., alias="takeCount")
    qty: str
    coins: str
    percent: str
    executed_at: int | None = Field(None, alias="executed_at")
    executed_price: str | None = Field(None, alias="executed_price")

    class Config:
        populate_by_name = True


class StopItem(BaseData):
    """Элемент стопа."""

    stop: float
    date: str


class ActiveCalcInfo(BaseData):
    """Информация об активном расчёте."""

    auto_take: float | None = Field(None, alias="autoTake")
    trailing_stop_count: float | None = Field(None, alias="trailingStopCount")
    exchange: str | None = None

    class Config:
        populate_by_name = True


class ChannelCalcInfo(BaseData):
    """Информация о расчёте канала."""

    time: int | None = Field(None, alias="time")
    without_stop: int | None = Field(None, alias="withoutStop")
    is_vote: int | None = Field(None, alias="isVote")
    is_pre_stop: int | None = Field(None, alias="isPreStop")

    class Config:
        populate_by_name = True


class CalcDetails(BaseData):
    """Полная информация о расчёте.

    Поля используют camelCase алиасы для соответствия API.
    """

    id: int
    vid: str
    deposit: float | str
    market: str
    category: str | None = None
    symbol: str | None = None
    quote: str | None = None
    status: str
    reverse: int
    open_price: float = Field(..., alias="openPrice")
    stop_loss: float = Field(..., alias="stopLoss")
    trading_style: str | None = Field(None, alias="tradingStyle")
    profit: float | None = Field(None, alias="profit")
    risk_value: float | str = Field(..., alias="riskValue")
    is_from_deposit: int = Field(..., alias="isFromDeposit")
    description: str | None = None
    comment: str | None = None
    comment2: str | None = None
    photo: str | None = None
    new_stop: str | None = Field(None, alias="newStop")
    is_open_price_changed: int = Field(..., alias="isOpenPriceChanged")
    created: int = Field(..., alias="c_created_")
    updated: int
    deal_time: int | None = Field(None, alias="dealTime")
    cancel_time: int | None = Field(None, alias="cancelTime")
    stat_time: int | None = Field(None, alias="statTime")
    ticker_sid: str | None = Field(None, alias="tickerSid")
    order_type: str | None = Field(None, alias="orderType")
    take: float | None = None
    take_profit: float | None = Field(None, alias="takeProfit")
    auto_take: float | None = Field(None, alias="autoTake")
    trailing_stop_count: int | None = Field(None, alias="trailingStopCount")
    exchange: str | None = Field(None, alias="exchange")
    rating: int | None = Field(None, alias="rating")
    active_calc: ActiveCalcInfo | None = Field(None, alias="activeCalc")
    channel_calc: ChannelCalcInfo | None = Field(None, alias="channelCalc")
    deal_price: DealPrice | None = Field(None, alias="dealPrice")
    trailing_stop: TrailingStopItem | None = Field(None, alias="trailingStop")
    fees: dict[str, Any]
    splits: list[SplitValue]
    splits_count: int = Field(..., alias="splitsCount")
    splits_hit_count: int = Field(..., alias="splitsHitCount")
    stops: list[StopItem]

    class Config:
        populate_by_name = True


class CalcListMeta(BaseData):
    """Метаинформация для ответа со списком расчётов."""

    page: int
    count: int
    total: int


class CalcListResponse(BaseModel):
    """Ответ для endpoint со списком расчётов."""

    success: bool
    data: list[ModelCalculation]
    meta: CalcListMeta


class CreateSplitValue(BaseData):
    """Значение разделения для запроса создания."""

    price: float
    qty: float
    coins: float
    percent: float
    take_count: int


class CalcCreateRequest(BaseData):
    """Данные запроса для создания расчёта."""

    deposit: str
    riskValue: str
    openPrice: float
    stopLoss: float
    market: str = "crypto"
    tpRatio: str = "3"
    symbol: str | None = None
    description: str | None = None
    comment: str | None = None
    photo: str | None = None
    pair: str | None = None
    reverse: bool = False
    newStop: float | None = None
    isFromDeposit: str = "0"
    status: str | None = None
    openedList: bool = False
    is_open_price_changed: bool = False
    ticker_sid: str | None = None
    orderType: str | None = None
    dealTime: int | None = None
    cancelTime: int | None = None
    statTime: int | None = None
    isChannel: bool = False
    isMarket: bool = False
    splitValues: list[CreateSplitValue] | None = None

    class Config:
        populate_by_name = True


class CalcCreateResponse(BaseData):
    """Данные ответа для создания расчёта."""

    id: int
    vid: str
    userId: int
    deposit: str
    riskValue: float
    openPrice: float
    stopLoss: float
    category: str | None = None
    market: str
    tpRatio: str
    roundCount: int | None = None
    tradingStyle: str | None = None
    symbol: str | None = None
    quote: str | None = None
    description: str | None = None
    comment: str | None = None
    photo: str | None = None
    pair: str | None = None
    reverse: bool
    newStop: float | None = None
    isFromDeposit: str
    status: str | None = None
    openedList: bool
    isOpenPriceChanged: bool
    ticker_sid: str | None = None
    orderType: str | None = None
    dealTime: int | None = None
    cancelTime: int | None = None
    statTime: int | None = None
    created: int
    updated: int
    is_update_raiting: bool = False
    splitValues: list[SplitValue]

    class Config:
        populate_by_name = True


class CalcCreateFullResponse(BaseModel):
    """Полный ответ для endpoint создания расчёта."""

    status: str
    response: CalcCreateResponse


class ActiveCalcCreateRequest(BaseData):
    """Запрос на создание активного расчёта."""

    calc_id: int
    exchange: str
    auto_take: float | None = None
    trailing_stop_count: int | None = None

    class Config:
        populate_by_name = True


class ActiveCalcCreateResponse(BaseData):
    """Ответ создания активного расчёта."""

    id: int
    calc_id: int
    auto_take: float | None = None
    trailing_stop_count: int | None = None
    exchange: str
    value: float | None = None

    class Config:
        populate_by_name = True


class ActiveCalcCreateFullResponse(BaseModel):
    """Полный ответ для endpoint создания активного расчёта."""

    status: str
    response: ActiveCalcCreateResponse


class CalcApiError(BaseApiError):
    """Исключение для ошибок API расчётов."""

    pass


class CalcService(BaseApiClient[ModelCalculation]):
    """
    Сервис для операций расчётов через API.

    Использует BaseApiClient для выполнения HTTP запросов
    с автоматической аутентификацией.
    """

    def __init__(self, base_url: str = API_AUTH_URL) -> None:
        super().__init__(base_url)

    async def get_calculations(
        self,
        user_id: int,
        sort_id: str = "desc",
        count: int = 10,
    ) -> CalcListResponse:
        """
        Получить список расчётов пользователя.

        Args:
            user_id: Telegram ID пользователя
            sort_id: Направление сортировки (asc/desc)
            count: Количество элементов для возврата

        Returns:
            CalcListResponse со списком расчётов в формате ModelCalculation

        Raises:
            CalcApiError: Если запрос не удался
        """
        try:
            data = await self._get(
                f"/calc/index-details?id={sort_id}&count={count}",
                user_id=user_id,
            )

            # Преобразуем CalcDetails в ModelCalculation
            raw_data = data.get("data", [])
            calculations = [
                calc_details_to_calculation(
                    CalcDetails.model_validate(item), user_id
                )
                for item in raw_data
            ]

            return CalcListResponse(
                success=data.get("success", True),
                data=calculations,
                meta=CalcListMeta(**data.get("meta", {})),
            )

        except BaseApiError as e:
            raise CalcApiError(
                message=f"Failed to get calculations: {e.message}",
                status_code=e.status_code,
                response_data=e.response_data,
            ) from e

    async def create_calculation(
        self,
        user_id: int,
        calc_data: CalcCreateRequest,
    ) -> CalcCreateFullResponse:
        """
        Создать новый расчёт.

        Args:
            user_id: Telegram ID пользователя
            calc_data: Данные расчёта для создания

        Returns:
            CalcCreateFullResponse с данными созданного расчёта

        Raises:
            CalcApiError: Если создание не удалось
        """
        payload = calc_data.model_dump(by_alias=True, exclude_none=True)
        # Добавляем обязательные поля
        payload.update({
            "category": "future",
            "quote": "USDT",
            "status": "WAIT",
            "openedList": False,
            "isOpenPriceChanged": False,
        })

        try:
            data = await self._post(
                "/calc/create",
                user_id=user_id,
                json=payload,
            )
            return CalcCreateFullResponse(**data)

        except BaseApiError as e:
            raise CalcApiError(
                message=f"Failed to create calculation: {e.message}",
                status_code=e.status_code,
                response_data=e.response_data,
            ) from e

    async def get_calculation(
        self,
        user_id: int,
        calc_id: int,
    ) -> ModelCalculation | None:
        """
        Получить детали расчёта по ID.

        Использует endpoint /calc/index-details и фильтрует по ID на стороне клиента,
        так как API не поддерживает прямую фильтрацию по ID.

        Args:
            user_id: Telegram ID пользователя
            calc_id: ID расчёта

        Returns:
            ModelCalculation с деталями расчёта или None, если не найден

        Raises:
            CalcApiError: Если запрос не удался
        """
        try:
            # Получаем список расчётов с большим count
            data = await self._get(
                f"/calc/index-details?count=1000",
                user_id=user_id,
            )

            raw_data = data.get("data", [])
            # Ищем расчёт по ID
            for item in raw_data:
                if item.get("id") == calc_id:
                    calc_details = CalcDetails.model_validate(item)
                    return calc_details_to_calculation(calc_details, user_id)

            # Расчёт не найден
            return None

        except BaseApiError as e:
            raise CalcApiError(
                message=f"Failed to get calculation {calc_id}: {e.message}",
                status_code=e.status_code,
                response_data=e.response_data,
            ) from e

    async def update_calculation(
        self,
        user_id: int,
        calc_id: int,
        **updates: Any,
    ) -> ModelCalculation:
        """
        Обновить расчёт.

        Args:
            user_id: Telegram ID пользователя
            calc_id: ID расчёта
            **updates: Поля для обновления

        Returns:
            ModelCalculation с обновлёнными данными

        Raises:
            CalcApiError: Если обновление не удалось
        """
        try:
            data = await self._post(
                f"/calc/update?id={calc_id}",
                user_id=user_id,
                json=updates,
            )
            calc_details = CalcDetails(**data)
            return calc_details_to_calculation(calc_details, user_id)

        except BaseApiError as e:
            raise CalcApiError(
                message=f"Failed to update calculation {calc_id}: {e.message}",
                status_code=e.status_code,
                response_data=e.response_data,
            ) from e

    async def create_active_calc(
        self,
        user_id: int,
        calc_id: int,
        exchange: str,
        auto_take: float | None = None,
        trailing_stop_count: int | None = None,
    ) -> ActiveCalcCreateResponse:
        """
        Создать/обновить запись активного расчёта.

        Args:
            user_id: Telegram ID пользователя
            calc_id: ID расчёта
            exchange: Биржа
            auto_take: Значение auto take
            trailing_stop_count: Количество трейлинг-стопов

        Returns:
            ActiveCalcCreateResponse с данными созданного активного расчёта

        Raises:
            CalcApiError: Если создание не удалось
        """
        try:
            payload = {
                "calcId": calc_id,
                "exchange": exchange,
            }
            if auto_take is not None:
                payload["autoTake"] = auto_take
            if trailing_stop_count is not None:
                payload["trailingStopCount"] = trailing_stop_count

            data = await self._post(
                "/active-calc/create",
                user_id=user_id,
                json=payload,
            )
            return ActiveCalcCreateResponse(**data["response"])

        except BaseApiError as e:
            raise CalcApiError(
                message=f"Failed to create active calc: {e.message}",
                status_code=e.status_code,
            ) from e


def calc_details_to_calculation(calc_details: CalcDetails, user_id: int) -> ModelCalculation:
    """
    Преобразовать CalcDetails из API в модель Calculation для использования в коде.

    Эта функция-адаптер конвертирует данные из формата API (camelCase)
    в формат, используемый в кодовой базе (PascalCase).

    Args:
        calc_details: Данные расчёта из API
        user_id: Telegram ID пользователя

    Returns:
        ModelCalculation: Модель расчёта для использования в коде
    """
    # Преобразуем splits из API в формат для Calculation
    split_values = None
    if calc_details.splits:
        split_values = [float(s.planned_qty)
                        for s in calc_details.splits if s.planned_qty]

    # Преобразуем tpRatio из строки в список чисел
    tp_ratio = []
    if calc_details.take:
        try:
            tp_ratio = [calc_details.take]
        except:
            tp_ratio = []

    # Формируем tool из ticker_sid или symbol
    tool = calc_details.ticker_sid or calc_details.symbol

    return ModelCalculation(
        id=calc_details.id,
        userId=user_id,
        profit=calc_details.profit or 0.0,
        inStat=False,  # API не возвращает это поле
        statDt=None,
        market=calc_details.market,  # type: ignore
        tradingType="margin",  # Значение по умолчанию
        isFromDeposit=bool(calc_details.is_from_deposit),
        tradingStyle=calc_details.trading_style,
        roundCount=None,  # API не возвращает это поле
        currency=calc_details.quote or "USDT",
        deposit=float(calc_details.deposit) if isinstance(
            calc_details.deposit, (int, float)) else 0,
        riskValue=float(calc_details.risk_value) if isinstance(
            calc_details.risk_value, (int, float)) else 0,
        openPrice=calc_details.open_price,
        stopLoss=calc_details.stop_loss,
        newStop=float(
            calc_details.new_stop) if calc_details.new_stop else None,
        isOpenPriceChanged=bool(calc_details.is_open_price_changed),
        tpRatio=tp_ratio,
        splitValues=split_values,
        forexInfo=None,  # API не возвращает это поле
        tool=tool,
        status=calc_details.status,  # type: ignore
        description=calc_details.description,
        photo=calc_details.photo,
        comment=calc_details.comment,
        openedList=False,  # API не возвращает это поле
        TrailingStops=None,  # API не возвращает это поле
        ActiveCalc=_convert_active_calc(
            calc_details.active_calc),  # type: ignore
        createdAt=None,  # API возвращает timestamp, а не строку
        dealAt=None,
        cancelAt=None,
    )


def _convert_active_calc(active_calc: ActiveCalcInfo) -> Optional[dict]:
    """
    Преобразовать ActiveCalcInfo в формат, ожидаемый моделью Calculation.

    Args:
        active_calc: Данные активного расчёта из API

    Returns:
        Словарь с данными активного расчёта или None
    """
    if not active_calc:
        return None

    # Если все поля None, возвращаем None (нет активного расчёта)
    if (active_calc.auto_take is None and
        active_calc.trailing_stop_count is None and
        not active_calc.exchange):
        return None

    # Формируем обмен в верхнем регистре или используем значение по умолчанию
    exchange = active_calc.exchange.upper() if active_calc.exchange else "BYBIT"

    return {
        "autoTake": active_calc.auto_take,
        "trailingStopCount": active_calc.trailing_stop_count,
        "autoStop": None,  # API не возвращает это поле
        "chMesIds": None,  # API не возвращает это поле
        "exchange": exchange,  # Должен быть "BYBIT" или "BINANCE"
    }


# Глобальный экземпляр сервиса расчётов
calc_service = CalcService()
