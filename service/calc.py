"""
Сервис расчётов для API calc endpoints.

Этот модуль предоставляет методы для операций расчётов, включая
получение списка расчётов и создание новых расчётов.
"""

import logging
from typing import Any

from pydantic import BaseModel
import aiohttp

from config_global import API_AUTH_URL
from service.auth import AuthApiError
from service.base import BaseData
from service.middleware import request_with_auth
from service.token_storage import token_storage

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
    risk_value: str
    open_price: float
    stop_loss: float
    # category: str | None = None
    market: str = 'crypto'
    tp_ratio: str = '3'
    # round_count: int
    # trading_style: str | None = None
    symbol: str | None = None
    # quote: str | None = None
    description: str | None = None
    comment: str | None = None
    photo: str | None = None
    pair: str | None = None
    reverse: bool = False
    new_stop: float | None = None
    is_from_deposit: str = "0"
    status: str | None = None
    opened_list: bool = False
    is_open_price_changed: bool = False
    ticker_sid: str | None = None
    order_type: str | None = None
    deal_time: int | None = None
    cancel_time: int | None = None
    stat_time: int | None = None
    is_channel: bool = False
    is_market: bool = False
    split_values: list[CreateSplitValue] | None = None

    class Config:
        populate_by_name = True


class CalcCreateResponse(BaseData):
    """Данные ответа для создания расчёта."""

    id: int
    vid: str
    user_id: int
    deposit: str
    risk_value: str
    open_price: float
    stop_loss: float
    category: str | None = None
    market: str
    tp_ratio: str
    round_count: int
    trading_style: str | None = None
    symbol: str | None = None
    quote: str | None = None
    description: str | None = None
    comment: str | None = None
    photo: str | None = None
    pair: str | None = None
    reverse: bool
    new_stop: float | None = None
    is_from_deposit: str
    status: str | None = None
    opened_list: bool
    is_open_price_changed: bool
    ticker_sid: str | None = None
    order_type: str | None = None
    deal_time: int | None = None
    cancel_time: int | None = None
    stat_time: int | None = None
    created: int
    updated: int
    is_update_raiting: bool
    split_values: list[SplitValue]

    class Config:
        populate_by_name = True


class CalcCreateFullResponse(BaseModel):
    """Полный ответ для endpoint создания расчёта."""

    status: str
    response: CalcCreateResponse


class CalcService:
    """
    Сервис для операций расчётов через API.

    Предоставляет асинхронные методы для:
    - Получения списка расчётов
    - Создания новых расчётов
    """

    def __init__(self, base_url: str = API_AUTH_URL) -> None:
        """
        Инициализировать сервис расчётов.

        Args:
            base_url: Базовый URL для API
        """
        self.base_url = base_url.rstrip("/")

    def _build_url(self, endpoint: str) -> str:
        """
        Построить полный URL для endpoint.

        Args:
            endpoint: Путь к API endpoint

        Returns:
            Полный URL
        """
        return f"{self.base_url}{endpoint}"

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
            AuthApiError: Если аутентификация не удалась
        """
        access_token = token_storage.get_access_token(user_id)
        if not access_token:
            raise AuthApiError("User not authenticated")

        url = self._build_url(
            f"/calc/index-details?id={sort_id}&count={count}")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        session = aiohttp.ClientSession()
        try:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if response.status in (401, 403):
                    await session.close()
                    # Используем middleware для повтора с обновлением токена
                    retry_response = await request_with_auth("GET", url, user_id, headers=headers)
                    data = await retry_response.json()
                    if retry_response.status >= 400:
                        raise AuthApiError(
                            message=data.get(
                                "message", "Failed to get calculations"),
                            status_code=retry_response.status,
                        )
                    return CalcListResponse(**data)

                if response.status >= 400:
                    raise AuthApiError(
                        message=data.get(
                            "message", "Failed to get calculations"),
                        status_code=response.status,
                    )

                return CalcListResponse(**data)

        except aiohttp.ClientError as e:
            logger.error(f"Network error during get calculations: {e}")
            raise AuthApiError("Network error during get calculations") from e
        finally:
            await session.close()

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
            AuthApiError: Если аутентификация не удалась или создание не удалось
        """
        access_token = token_storage.get_access_token(user_id)
        if not access_token:
            raise AuthApiError("User not authenticated")

        url = self._build_url("/calc/create")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = calc_data.model_dump(by_alias=True, exclude_none=True)

        session = aiohttp.ClientSession()
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()

                if response.status in (401, 403):
                    await session.close()
                    # Используем middleware для повтора с обновлением токена
                    retry_response = await request_with_auth("POST", url, user_id, json=payload, headers=headers)
                    data = await retry_response.json()
                    if retry_response.status >= 400:
                        raise AuthApiError(
                            message=data.get(
                                "message", "Failed to create calculation"),
                            status_code=retry_response.status,
                        )
                    return CalcCreateFullResponse(**data)

                if response.status >= 400:
                    raise AuthApiError(
                        message=data.get(
                            "message", "Failed to create calculation"),
                        status_code=response.status,
                    )

                return CalcCreateFullResponse(**data)

        except aiohttp.ClientError as e:
            logger.error(f"Network error during create calculation: {e}")
            raise AuthApiError(
                "Network error during create calculation") from e
        finally:
            await session.close()


# Глобальный экземпляр сервиса расчётов
calc_service = CalcService()


async def get_calculations(
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
        AuthApiError: Если аутентификация не удалась
    """
    return await calc_service.get_calculations(user_id, sort_id, count)


async def create_calculation(
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
        AuthApiError: Если аутентификация не удалась или создание не удалось
    """
    return await calc_service.create_calculation(user_id, calc_data)
