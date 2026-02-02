"""
Базовый API клиент для всех сервисов.

Предоставляет единый интерфейс для HTTP запросов с автоматическим
обновлением токена, логированием и обработкой ошибок.
"""

import logging
from abc import ABC
from typing import Any, TypeVar, Generic

import aiohttp

from config_global import API_AUTH_URL
from service.auth import AuthApiError
from service.base import BaseData
from service.middleware import request_with_auth
from service.token_storage import token_storage

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseData)


class BaseApiError(Exception):
    """Базовое исключение для API ошибок."""

    def __init__(self, message: str, status_code: int | None = None, response_data: dict[str, Any] | None = None) -> None:
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (status: {self.status_code})"
        return self.message


class BaseApiClient(ABC, Generic[T]):
    """
    Базовый класс для API клиентов.

    Предоставляет общие методы для выполнения HTTP запросов
    с автоматической аутентификацией и обновлением токена.
    """

    base_url: str = API_AUTH_URL

    def __init__(self, base_url: str | None = None) -> None:
        """
        Инициализировать API клиент.

        Args:
            base_url: Опциональный базовый URL (переопределяет base_url класса)
        """
        self.base_url = (base_url or self.base_url).rstrip("/")

    def _build_url(self, endpoint: str) -> str:
        """Построить полный URL для endpoint."""
        return f"{self.base_url}{endpoint}"

    def _get_default_headers(self, user_id: int) -> dict[str, str]:
        """Получить заголовки по умолчанию для запроса."""
        access_token = token_storage.get_access_token(user_id)
        if not access_token:
            raise AuthApiError("No access token found for user")

        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        user_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Выполнить API запрос с автоматическим обновлением токена.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint путь
            user_id: ID пользователя для аутентификации
            **kwargs: Дополнительные аргументы для запроса

        Returns:
            Словарь с данными ответа

        Raises:
            BaseApiError: При ошибке API
        """
        url = self._build_url(endpoint)
        headers = kwargs.pop("headers", {})
        headers.update(self._get_default_headers(user_id))
        kwargs["headers"] = headers

        try:
            session, data = await request_with_auth(method, url, user_id, **kwargs)

            # Получаем статус из данных (если API возвращает его)
            # или проверяем наличие поля 'success'
            if not data.get("success", True):
                raise BaseApiError(
                    message=data.get("message", f"{method} {endpoint} failed"),
                    status_code=data.get("status"),
                    response_data=data,
                )

            return data

        except AuthApiError as e:
            logger.error(f"Auth error during {method} {endpoint}: {e}")
            raise BaseApiError(
                f"Authentication failed for {method} {endpoint}") from e
        except aiohttp.ClientError as e:
            logger.error(f"Network error during {method} {endpoint}: {e}")
            raise BaseApiError(
                f"Network error during {method} {endpoint}") from e
        finally:
            if 'session' in locals():
                await session.close()  # type: ignore

    async def _get(
        self,
        endpoint: str,
        user_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполнить GET запрос."""
        return await self._request("GET", endpoint, user_id, **kwargs)

    async def _post(
        self,
        endpoint: str,
        user_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполнить POST запрос."""
        return await self._request("POST", endpoint, user_id, **kwargs)

    async def _put(
        self,
        endpoint: str,
        user_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполнить PUT запрос."""
        return await self._request("PUT", endpoint, user_id, **kwargs)

    async def _patch(
        self,
        endpoint: str,
        user_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполнить PATCH запрос."""
        return await self._request("PATCH", endpoint, user_id, **kwargs)

    async def _delete(
        self,
        endpoint: str,
        user_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполнить DELETE запрос."""
        return await self._request("DELETE", endpoint, user_id, **kwargs)


class PublicApiClient(BaseApiClient[T]):
    """
    Базовый класс для публичных API клиентов (без аутентификации).

    Используется для endpoints, которые не требуют токена аутентификации.
    """

    def _get_default_headers(self, user_id: int | None = None) -> dict[str, str]:
        """Получить заголовки по умолчанию для публичного запроса."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        user_id: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Выполнить публичный API запрос без аутентификации.

        Args:
            method: HTTP метод
            endpoint: API endpoint путь
            user_id: Игнорируется для публичных запросов
            **kwargs: Дополнительные аргументы

        Returns:
            Словарь с данными ответа

        Raises:
            BaseApiError: При ошибке API
        """
        url = self._build_url(endpoint)
        headers = kwargs.pop("headers", {})
        headers.update(self._get_default_headers())
        kwargs["headers"] = headers

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as response:
                    data = await response.json()

                    if response.status >= 400:
                        raise BaseApiError(
                            message=data.get(
                                "message", f"{method} {endpoint} failed"),
                            status_code=response.status,
                            response_data=data,
                        )

                    return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error during {method} {endpoint}: {e}")
            raise BaseApiError(
                f"Network error during {method} {endpoint}") from e
