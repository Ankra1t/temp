"""
Сервис аутентификации для API auth endpoints.

Этот модуль предоставляет методы для операций аутентификации пользователей, включая
вход, обновление токена, выход и управление сессиями.
"""

import logging
from typing import Optional

import aiohttp

from config_global import API_AUTH_KEY, API_AUTH_URL
from service.base import (
    LoginData,
    LoginResponse,
    RefreshResponse,
    SessionResponse,
    TokenPair,
)
from service.token_storage import token_storage

logger = logging.getLogger(__name__)


class AuthApiError(Exception):
    """Исключение, возникающее при ошибках API аутентификации."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthService:
    def __init__(self, base_url: str = API_AUTH_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    async def login(
        self, tgId: int
    ) -> LoginResponse:
        session = await self._get_session()
        url = self._build_url("/auth/tg")

        payload = {
            "tgId": tgId
        }

        try:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json",
                         'X-API-KEY': API_AUTH_KEY},
            ) as response:
                data = await response.json()

                if response.status >= 400:
                    raise AuthApiError(
                        message=data.get("message", "Authentication failed"),
                        status_code=response.status,
                    )

                return LoginResponse(**data)

        except aiohttp.ClientError as e:
            logger.error(f"Network error during login: {e}")
            raise AuthApiError("Network error during authentication") from e

    async def refresh(self, refresh_token: str) -> RefreshResponse:
        session = await self._get_session()
        url = self._build_url("/auth/refresh")

        payload = {"refreshToken": refresh_token}

        try:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                data = await response.json()

                if response.status >= 400:
                    raise AuthApiError(
                        message=data.get("message", "Token refresh failed"),
                        status_code=response.status,
                    )

                return RefreshResponse(**data)

        except aiohttp.ClientError as e:
            logger.error(f"Network error during token refresh: {e}")
            raise AuthApiError("Network error during token refresh") from e

    async def get_session(self, access_token: str) -> SessionResponse:
        session = await self._get_session()
        url = self._build_url("/users/me")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if response.status >= 400:
                    raise AuthApiError(
                        message=data.get("message", "Failed to get session"),
                        status_code=response.status,
                    )

                return SessionResponse(**data)

        except aiohttp.ClientError as e:
            logger.error(f"Network error during session retrieval: {e}")
            raise AuthApiError("Network error during session retrieval") from e


# Глобальный экземпляр сервиса аутентификации
auth_service = AuthService()


async def register_user_from_tg(
    tgId: int,
) -> LoginData:
    response = await auth_service.login(tgId)

    if not response.success or response.data is None:
        raise AuthApiError("Authentication failed")

    tokens = TokenPair(
        access_token=response.data.access_token,
        refresh_token=response.data.refresh_token,
    )

    token_storage.set(tgId, tokens, ttl_seconds=3600)

    logger.info(f"User {tgId} authenticated successfully")

    return response.data
