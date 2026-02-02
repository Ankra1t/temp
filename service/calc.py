"""
Сервис расчётов для API calc endpoints.

Этот модуль предоставляет методы для операций расчётов, включая
получение списка расчётов и создание новых расчётов.
"""

import logging
from typing import Any

from pydantic import BaseModel

from config_global import API_AUTH_URL
from service.base import BaseData
from service.base_api import BaseApiClient, BaseApiError

logger = logging.getLogger(__name__)


# Модели ответов для API расчётов


class DealPrice(BaseData):
    """Информация о цене сделки."""

    min_price: float | None = None
    min_price_dt: int | None = None
    max_price: float | None = None
    max_price_dt: int | None = None

    class Config:
        populate_by_name = True


class TrailingStopItem(BaseData):
    """Значение трейлинг-стопа."""

    value: float
    ts_created: int


class SplitFees(BaseData):
    """Распределение комиссий при разделении."""

    open_alloc: str | None = None
    funding_alloc: str | None = None
    settle_alloc: str | None = None
    total: str | None = None


class SplitValue(BaseData):
    """Значение разделения (take profit)."""

    id: str
    price: str
    planned_qty: str
    filled_qty: str
    status: str
    created_at: int
    updated_at: int
    fees: SplitFees
    take_count: str
    qty: str
    coins: str
    percent: str
    executed_at: int | None = None
    executed_price: str | None = None

    class Config:
        populate_by_name = True


class StopItem(BaseData):
    """Элемент стопа."""

    stop: float
    date: str


class ActiveCalcInfo(BaseData):
    """Информация об активном расчёте."""

    auto_take: float | None = None
    trailing_stop_count: float | None = None
    exchange: str | None = None

    class Config:
        populate_by_name = True


class ChannelCalcInfo(BaseData):
    """Информация о расчёте канала."""

    time: int
    without_stop: int
    is_vote: int
    is_pre_stop: int

    class Config:
        populate_by_name = True


class CalcDetails(BaseData):
    """Полная информация о расчёте."""

    id: int
    vid: str
    deposit: float | str
    market: str
    category: str | None = None
    symbol: str | None = None
    quote: str | None = None
    status: str
    reverse: int
    open_price: float
    stop_loss: float
    trading_style: str | None = None
    profit: float
    risk_value: float | str
    is_from_deposit: int
    description: str | None = None
    comment: str | None = None
    comment2: str | None = None
    photo: str | None = None
    new_stop: str | None = None
    is_open_price_changed: int
    created: int
    updated: int
    deal_time: int | None = None
    cancel_time: int | None = None
    stat_time: int | None = None
    ticker_sid: str | None = None
    order_type: str | None = None
    take: float | None = None
    take_profit: float | None = None
    auto_take: float | None = None
    trailing_stop_count: int
    exchange: str
    rating: int
    active_calc: ActiveCalcInfo
    channel_calc: ChannelCalcInfo
    deal_price: DealPrice | None = None
    trailing_stop: TrailingStopItem | None = None
    fees: dict[str, Any]
    splits: list[SplitValue]
    splits_count: int
    splits_hit_count: int
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
    data: list[CalcDetails]
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
    opened_list: bool = False
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
    isUpdateRaiting: bool = False
    splitValues: list[SplitValue]

    class Config:
        populate_by_name = True


class CalcCreateFullResponse(BaseModel):
    """Полный ответ для endpoint создания расчёта."""

    status: str
    response: CalcCreateResponse


class CalcApiError(BaseApiError):
    """Исключение для ошибок API расчётов."""

    pass


class CalcService(BaseApiClient[CalcDetails]):
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
            CalcListResponse со списком расчётов и метаинформацией

        Raises:
            CalcApiError: Если запрос не удался
        """
        try:
            data = await self._get(
                f"/calc/index-details?id={sort_id}&count={count}",
                user_id=user_id,
            )
            return CalcListResponse(**data)

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
    ) -> CalcDetails:
        """
        Получить детали расчёта по ID.

        Args:
            user_id: Telegram ID пользователя
            calc_id: ID расчёта

        Returns:
            CalcDetails с деталями расчёта

        Raises:
            CalcApiError: Если запрос не удался
        """
        try:
            data = await self._get(
                f"/calc/details?id={calc_id}",
                user_id=user_id,
            )
            return CalcDetails(**data)

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
    ) -> CalcDetails:
        """
        Обновить расчёт.

        Args:
            user_id: Telegram ID пользователя
            calc_id: ID расчёта
            **updates: Поля для обновления

        Returns:
            CalcDetails с обновлёнными данными

        Raises:
            CalcApiError: Если обновление не удалось
        """
        try:
            data = await self._post(
                f"/calc/update?id={calc_id}",
                user_id=user_id,
                json=updates,
            )
            return CalcDetails(**data)

        except BaseApiError as e:
            raise CalcApiError(
                message=f"Failed to update calculation {calc_id}: {e.message}",
                status_code=e.status_code,
                response_data=e.response_data,
            ) from e


# Глобальный экземпляр сервиса расчётов
calc_service = CalcService()
