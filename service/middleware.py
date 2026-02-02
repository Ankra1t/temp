"""
Middleware для обновления токена при API запросах.

Этот модуль предоставляет middleware для обработки обновления токена
во время API запросов, обеспечивая корректное состояние аутентификации.
"""

import logging
from typing import Any

from aiohttp import ClientSession

from service.auth import auth_service, AuthApiError
from service.token_storage import token_storage, TokenPair

logger = logging.getLogger(__name__)


async def request_with_auth(
    method: str,
    url: str,
    user_id: int,
    *args: Any,
    **kwargs: Any,
) -> tuple[ClientSession, dict[str, Any]]:
    """
    Выполнить аутентифицированный API запрос с автоматическим обновлением токена при 401/403.

    Args:
        method: HTTP метод (GET, POST, и т.д.)
        url: URL запроса
        user_id: ID пользователя для поиска токена
        *args: Дополнительные позиционные аргументы для запроса
        **kwargs: Дополнительные именованные аргументы для запроса

    Returns:
        Кортеж (session, data) - сессия и данные ответа

    Raises:
        AuthApiError: Если аутентификация не удалась
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
            data = await response.json()

            # Обработка истёкшего токена - обновить и повторить один раз
            if response.status in (401, 403):
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

                    async with session.request(method, url, *args, **kwargs) as retry_response:
                        retry_data = await retry_response.json()

                        # Если всё ещё получаем 401/403, аутентификация не удалась
                        if retry_response.status in (401, 403):
                            token_storage.remove(user_id)
                            raise AuthApiError(
                                f"Authentication failed after token refresh (status: {retry_response.status})"
                            )

                        return session, retry_data

                except AuthApiError as e:
                    logger.error(f"Failed to refresh token for user {user_id}: {e}")
                    token_storage.remove(user_id)
                    raise

            return session, data

    except Exception:
        await session.close()
        raise
