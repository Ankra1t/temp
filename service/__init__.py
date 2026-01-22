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
from service.user_settings_storage import (
    UserSettings,
    UserSettingsStorage,
    user_settings_storage,
)
from service.middleware import (
    RefreshTokenMiddleware,
    request_with_auth,
    get_valid_access_token,
)
from service.calc import (
    # Модели расчётов
    DealPrice,
    TrailingStopItem,
    SplitFees,
    SplitValue,
    StopItem,
    ActiveCalcInfo,
    ChannelCalcInfo,
    CalcDetails,
    CreateSplitValue,
    CalcCreateRequest,
    CalcCreateResponse,
    # Типы ответов расчётов
    CalcListResponse,
    CalcCreateFullResponse,
    # Сервис расчётов
    CalcService,
    calc_service,
    # Функции расчётов
    get_calculations,
    create_calculation,
)

__all__ = [
    # Базовые модели
    "BaseResponse",
    "BaseData",
    "BaseMeta",
    "ApiResponse",
    "TokenPair",
    "TokenType",
    "ApiUser",
    # Типы ответов
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
    # Сервис аутентификации
    "AuthService",
    "auth_service",
    "AuthApiError",
    "register_user_from_tg",
    "get_user_tokens",
    "ensure_authenticated",
    "logout_user",
    # Хранилище токенов
    "TokenStorage",
    "token_storage",
    # Хранилище настроек пользователей
    "UserSettings",
    "UserSettingsStorage",
    "user_settings_storage",
    # Middleware
    "RefreshTokenMiddleware",
    "request_with_auth",
    "get_valid_access_token",
    # Модели расчётов
    "DealPrice",
    "TrailingStopItem",
    "SplitFees",
    "SplitValue",
    "StopItem",
    "ActiveCalcInfo",
    "ChannelCalcInfo",
    "CalcDetails",
    "CreateSplitValue",
    "CalcCreateRequest",
    "CalcCreateResponse",
    # Типы ответов расчётов
    "CalcListResponse",
    "CalcCreateFullResponse",
    # Сервис расчётов
    "CalcService",
    "calc_service",
    "get_calculations",
    "create_calculation",
]
