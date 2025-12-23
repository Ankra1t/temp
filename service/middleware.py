"""
Refresh token middleware for API requests.

This module provides a middleware for handling token refresh
during API requests, ensuring valid authentication state.
"""

import logging
from typing import Optional, Callable, Any

from aiohttp import ClientSession, ClientResponse

from service.auth import auth_service, AuthApiError
from service.token_storage import token_storage, TokenPair

logger = logging.getLogger(__name__)


class RefreshTokenMiddleware:
    """
    Middleware for handling token refresh during API requests.

    Automatically refreshes expired tokens when receiving 401/403 errors
    and retries failed requests with new authentication credentials.
    """

    def __init__(self, get_user_id: Callable[[int], int]) -> None:
        """
        Initialize refresh token middleware.

        Args:
            get_user_id: Function to extract user ID from request context
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
        Execute request with automatic token refresh on 401/403 errors.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            user_id: User ID for token lookup
            *args: Additional positional arguments for request
            **kwargs: Additional keyword arguments for request

        Returns:
            ClientResponse from the API

        Raises:
            AuthApiError: If authentication fails after refresh attempt
        """
        # Get initial access token
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
        Execute request with token refresh on 401/403.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            user_id: User ID for token lookup
            access_token: Current access token
            *args: Additional positional arguments for request
            **kwargs: Additional keyword arguments for request

        Returns:
            ClientResponse from the API

        Raises:
            AuthApiError: If authentication fails after refresh attempt
        """
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        kwargs["headers"] = headers

        session = ClientSession()
        try:
            async with session.request(method, url, *args, **kwargs) as response:
                # Check if token expired (401 or 403)
                if response.status in (401, 403):
                    # Try to refresh token and retry once
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
        Refresh token and retry request once.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            user_id: User ID for token lookup
            *args: Additional positional arguments for request
            **kwargs: Additional keyword arguments for request

        Returns:
            ClientResponse from the API

        Raises:
            AuthApiError: If refresh fails or retry still returns 401/403
        """
        refresh_token = token_storage.get_refresh_token(user_id)
        if not refresh_token:
            raise AuthApiError("No refresh token available")

        try:
            # Attempt to refresh token
            refresh_response = await auth_service.refresh(refresh_token)
            if not refresh_response.success or not refresh_response.data:
                raise AuthApiError("Token refresh failed")

            # Update stored tokens
            new_tokens = TokenPair(
                access_token=refresh_response.data.access_token,
                refresh_token=refresh_response.data.refresh_token,
            )
            token_storage.set(user_id, new_tokens, ttl_seconds=3600)

            # Retry request with new token
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {new_tokens.access_token}"
            kwargs["headers"] = headers

            session = ClientSession()
            try:
                async with session.request(method, url, *args, **kwargs) as retry_response:
                    # If still getting 401/403, authentication has failed
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
    Make an authenticated API request with automatic token refresh on 401/403.

    This is a convenience function that handles token refresh logic
    for individual API requests. Refresh is only attempted when
    the server returns 401 or 403 status codes.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        user_id: User ID for token lookup
        *args: Additional positional arguments for request
        **kwargs: Additional keyword arguments for request

    Returns:
        ClientResponse from the API

    Raises:
        AuthApiError: If authentication fails

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
            # Handle expired token - refresh and retry once
            if response.status in (401, 403):
                await session.close()

                refresh_token = token_storage.get_refresh_token(user_id)
                if not refresh_token:
                    raise AuthApiError("No refresh token available")

                try:
                    # Attempt to refresh token
                    refresh_response = await auth_service.refresh(refresh_token)
                    if not refresh_response.success or not refresh_response.data:
                        raise AuthApiError("Token refresh failed")

                    # Update stored tokens
                    new_tokens = TokenPair(
                        access_token=refresh_response.data.access_token,
                        refresh_token=refresh_response.data.refresh_token,
                    )
                    token_storage.set(user_id, new_tokens, ttl_seconds=3600)

                    # Retry request with new token
                    headers["Authorization"] = f"Bearer {new_tokens.access_token}"
                    kwargs["headers"] = headers

                    session = ClientSession()
                    async with session.request(method, url, *args, **kwargs) as retry_response:
                        # If still getting 401/403, authentication has failed
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
    Get a valid access token for a user.

    Note: This only checks local expiration time. The actual request
    may still fail with 401/403 if the server-side token has expired.
    Use request_with_auth() for automatic token refresh on 401/403 errors.

    Args:
        user_id: User ID for token lookup

    Returns:
        Valid access token string or None if no token exists
    """
    # Return current token if exists (don't pre-refresh)
    return token_storage.get_access_token(user_id)
