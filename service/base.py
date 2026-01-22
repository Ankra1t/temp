"""
Базовые модели и типы для API ответов.

Этот модуль определяет общую структуру для всех API ответов,
включая базовые классы и специфические модели данных для различных endpoints.
"""

from typing import Optional, Any, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum


class BaseMeta(BaseModel):
    """Базовые метаданные для API ответов."""

    pass


class BaseData(BaseModel):
    """Базовая модель данных для API ответов."""

    pass


T = TypeVar("T", bound=BaseData)


class BaseResponse(BaseModel, Generic[T]):
    success: bool = Field(
        description="Indicates if the request was successful")
    data: T = Field(description="Response payload")
    # meta: Optional[BaseMeta] = Field(
    #     default=None, description="Additional metadata")


class UserConfig(BaseModel):
    pass


class ApiUser(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None


class LoginData(BaseData):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    user: ApiUser


class RefreshData(BaseData):
    """Данные ответа для endpoint обновления токена."""

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")


class UserData(BaseData):
    """Данные профиля пользователя из endpoint сессии."""

    id: int
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    referral_code: Optional[str] = Field(alias="referralCode", default=None)
    referrer_id: Optional[int] = Field(alias="referrerId", default=None)


class SessionData(BaseData):
    """Данные ответа для endpoint session/me."""

    id: int
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    referral_code: Optional[str] = Field(alias="referralCode", default=None)
    referrer_id: Optional[int] = Field(alias="referrerId", default=None)


class LogoutData(BaseData):
    """Данные ответа для endpoint выхода."""

    message: str


# Псевдонимы типов для полных типов ответов
ApiResponse = BaseResponse[BaseData]
LoginResponse = BaseResponse[LoginData]
RefreshResponse = BaseResponse[RefreshData]
UserResponse = BaseResponse[UserData]
SessionResponse = BaseResponse[SessionData]
LogoutResponse = BaseResponse[LogoutData]


class TokenType(str, Enum):
    """Типы токенов для хранения и валидации."""

    ACCESS = "access_token"
    REFRESH = "refresh_token"


class TokenPair(BaseModel):
    """Пара из access и refresh токенов."""

    access_token: str
    refresh_token: str

    class Config:
        populate_by_name = True

        field_aliases = {
            "access_token": "accessToken",
            "refresh_token": "refreshToken",
        }
