"""
Service module for API requests.

This module provides asynchronous HTTP clients for communicating with external APIs,
including authentication, data retrieval, and other operations.
"""

from service.base import (
    BaseResponse,
    BaseData,
    BaseMeta,
    ApiResponse,
    LoginData,
    RefreshData,
    UserData,
    SessionData,
    LogoutData,
    TokenPair,
    TokenType,
    LoginResponse,
    RefreshResponse,
    UserResponse,
    SessionResponse,
    LogoutResponse,
    ApiUser,
)
from service.auth import (
    AuthService,
    auth_service,
    AuthApiError,
    register_user_from_tg,
    get_user_tokens,
    ensure_authenticated,
    logout_user,
)
from service.token_storage import TokenStorage, token_storage
from service.middleware import (
    RefreshTokenMiddleware,
    request_with_auth,
    get_valid_access_token,
)

__all__ = [
    # Base models
    "BaseResponse",
    "BaseData",
    "BaseMeta",
    "ApiResponse",
    "TokenPair",
    "TokenType",
    "ApiUser",
    # Response types
    "LoginData",
    "RefreshData",
    "UserData",
    "SessionData",
    "LogoutData",
    "LoginResponse",
    "RefreshResponse",
    "UserResponse",
    "SessionResponse",
    "LogoutResponse",
    # Auth service
    "AuthService",
    "auth_service",
    "AuthApiError",
    "register_user_from_tg",
    "get_user_tokens",
    "ensure_authenticated",
    "logout_user",
    # Token storage
    "TokenStorage",
    "token_storage",
    # Middleware
    "RefreshTokenMiddleware",
    "request_with_auth",
    "get_valid_access_token",
]
