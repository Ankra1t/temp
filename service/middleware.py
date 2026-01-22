"""
Middleware для обновления токена при API запросах.

Этот модуль предоставляет middleware для обработки обновления токена
во время API запросов, обеспечивая корректное состояние аутентификации.
"""

import logging
from typing import Optional, Callable, Any

from aiohttp import ClientSession, ClientResponse

from service.auth import auth_service, AuthApiError
from service.token_storage import token_storage, TokenPair

logger = logging.getLogger(__name__)


class RefreshTokenMiddleware:
    """
    Middleware для обработки обновления токена во время API запросов.

    Автоматически обновляет просроченные токены при получении ошибок 401/403
    и повторяет неудачные запросы с новыми учётными данными аутентификации.
    """

    def __init__(self, get_user_id: Callable[[int], int]) -> None:
        """
        Инициализировать middleware для обновления токена.

        Args:
            get_user_id: Функция для извлечения ID пользователя из контекста запроса
        """
        self.get_user_id = get_user_id

    async def __call__(
        self,
        method: str,
        url: str,
        user_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> ClientResponse:
        """
        Выполнить запрос с автоматическим обновлением токена при ошибках 401/403.

        Args:
            method: HTTP метод (GET, POST, и т.д.)
            url: URL запроса
            user_id: ID пользователя для поиска токена
            *args: Дополнительные позиционные аргументы для запроса
            **kwargs: Дополнительные именованные аргументы для запроса

        Returns:
            ClientResponse из API

        Raises:
            AuthApiError: Если аутентификация не удалась после попытки обновления
        """
        # Получить начальный access токен
        access_token = token_storage.get_access_token(user_id)

        if not access_token:
            raise AuthApiError("No access token found for user")

        return await self._execute_request(
            method, url, user_id, access_token, *args, **kwargs
        )

    async def _execute_request(
        self,
        method: str,
        url: str,
        user_id: int,
        access_token: str,
        *args: Any,
        **kwargs: Any,
    ) -> ClientResponse:
        """
        Выполнить запрос с обновлением токена при 401/403.

        Args:
            method: HTTP метод (GET, POST, и т.д.)
            url: URL запроса
            user_id: ID пользователя для поиска токена
            access_token: Текущий access токен
            *args: Дополнительные позиционные аргументы для запроса
            **kwargs: Дополнительные именованные аргументы для запроса

        Returns:
            ClientResponse из API

        Raises:
            AuthApiError: Если аутентификация не удалась после попытки обновления
        """
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        kwargs["headers"] = headers

        session = ClientSession()
        try:
            async with session.request(method, url, *args, **kwargs) as response:
                # Проверить, истёк ли токен (401 или 403)
                if response.status in (401, 403):
                    # Попробовать обновить токен и повторить один раз
                    return await self._refresh_and_retry(
                        method, url, user_id, *args, **kwargs
                    )

                return response

        finally:
            await session.close()

    async def _refresh_and_retry(
        self,
        method: str,
        url: str,
        user_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> ClientResponse:
        """
        Обновить токен и повторить запрос один раз.

        Args:
            method: HTTP метод (GET, POST, и т.д.)
            url: URL запроса
            user_id: ID пользователя для поиска токена
            *args: Дополнительные позиционные аргументы для запроса
            **kwargs: Дополнительные именованные аргументы для запроса

        Returns:
            ClientResponse из API

        Raises:
            AuthApiError: Если обновление не удалось или повторная попытка всё ещё возвращает 401/403
        """
        refresh_token = token_storage.get_refresh_token(user_id)
        if not refresh_token:
            raise AuthApiError("No refresh token available")

        try:
            # Попытка обновить токен
            refresh_response = await auth_service.refresh(refresh_token)
            if not refresh_response.success or not refresh_response.data:
                raise AuthApiError("Token refresh failed")

            # Обновить сохранённые токены
            new_tokens = TokenPair(
                access_token=refresh_response.data.access_token,
                refresh_token=refresh_response.data.refresh_token,
            )
            token_storage.set(user_id, new_tokens, ttl_seconds=3600)

            # Повторить запрос с новым токеном
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {new_tokens.access_token}"
            kwargs["headers"] = headers

            session = ClientSession()
            try:
                async with session.request(method, url, *args, **kwargs) as retry_response:
                    # Если всё ещё получаем 401/403, аутентификация не удалась
                    if retry_response.status in (401, 403):
                        token_storage.remove(user_id)
                        raise AuthApiError(
                            f"Authentication failed after token refresh (status: {retry_response.status})"
                        )
                    return retry_response

            finally:
                await session.close()

        except AuthApiError as e:
            logger.error(f"Failed to refresh token for user {user_id}: {e}")
            token_storage.remove(user_id)
            raise


async def request_with_auth(
    method: str,
    url: str,
    user_id: int,
    *args: Any,
    **kwargs: Any,
) -> ClientResponse:
    """
    Выполнить аутентифицированный API запрос с автоматическим обновлением токена при 401/403.

    Это удобная функция, которая обрабатывает логику обновления токена
    для отдельных API запросов. Обновление выполняется только когда
    сервер возвращает коды статуса 401 или 403.

    Args:
        method: HTTP метод (GET, POST, и т.д.)
        url: URL запроса
        user_id: ID пользователя для поиска токена
        *args: Дополнительные позиционные аргументы для запроса
        **kwargs: Дополнительные именованные аргументы для запроса

    Returns:
        ClientResponse из API

    Raises:
        AuthApiError: Если аутентификация не удалась

    Example:
        response = await request_with_auth(
            "GET",
            "https://api.example.com/data",
            user_id=12345
        )
        data = await response.json()
    """
    access_token = token_storage.get_access_token(user_id)

    if not access_token:
        raise AuthApiError("No access token found for user")

    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"Bearer {access_token}"
    kwargs["headers"] = headers

    session = ClientSession()
    try:
        async with session.request(method, url, *args, **kwargs) as response:
            # Обработка истёкшего токена - обновить и повторить один раз
            if response.status in (401, 403):
                await session.close()

                refresh_token = token_storage.get_refresh_token(user_id)
                if not refresh_token:
                    raise AuthApiError("No refresh token available")

                try:
                    # Попытка обновить токен
                    refresh_response = await auth_service.refresh(refresh_token)
                    if not refresh_response.success or not refresh_response.data:
                        raise AuthApiError("Token refresh failed")

                    # Обновить сохранённые токены
                    new_tokens = TokenPair(
                        access_token=refresh_response.data.access_token,
                        refresh_token=refresh_response.data.refresh_token,
                    )
                    token_storage.set(user_id, new_tokens, ttl_seconds=3600)

                    # Повторить запрос с новым токеном
                    headers["Authorization"] = f"Bearer {new_tokens.access_token}"
                    kwargs["headers"] = headers

                    session = ClientSession()
                    async with session.request(method, url, *args, **kwargs) as retry_response:
                        # Если всё ещё получаем 401/403, аутентификация не удалась
                        if retry_response.status in (401, 403):
                            token_storage.remove(user_id)
                            raise AuthApiError(
                                f"Authentication failed after token refresh (status: {retry_response.status})"
                            )
                        return retry_response

                except AuthApiError as e:
                    logger.error(f"Failed to refresh token for user {user_id}: {e}")
                    token_storage.remove(user_id)
                    raise

            return response

    finally:
        await session.close()


async def get_valid_access_token(user_id: int) -> Optional[str]:
    """
    Получить действующий access токен для пользователя.

    Note: Эта функция проверяет только локальное время истечения. Фактический запрос
    может всё ещё завершиться неудачей с 401/403, если токен на стороне сервера истёк.
    Используйте request_with_auth() для автоматического обновления токена при ошибках 401/403.

    Args:
        user_id: ID пользователя для поиска токена

    Returns:
        Действующий access токен или None, если токен не существует
    """
    # Вернуть текущий токен, если существует (не обновлять заранее)
    return token_storage.get_access_token(user_id)
