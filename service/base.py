"""
Base models and types for API responses.

This module defines the common structure for all API responses,
including base classes and specific data models for different endpoints.
"""

from typing import Optional, Any, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum


class BaseMeta(BaseModel):
    """Base metadata for API responses."""

    pass


class BaseData(BaseModel):
    """Base data model for API responses."""

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
    """Response data for refresh token endpoint."""

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")


class UserData(BaseData):
    """User profile data from session endpoint."""

    id: int
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    referral_code: Optional[str] = Field(alias="referralCode", default=None)
    referrer_id: Optional[int] = Field(alias="referrerId", default=None)


class SessionData(BaseData):
    """Response data for session/me endpoint."""

    id: int
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    referral_code: Optional[str] = Field(alias="referralCode", default=None)
    referrer_id: Optional[int] = Field(alias="referrerId", default=None)


class LogoutData(BaseData):
    """Response data for logout endpoint."""

    message: str


# Type aliases for complete response types
ApiResponse = BaseResponse[BaseData]
LoginResponse = BaseResponse[LoginData]
RefreshResponse = BaseResponse[RefreshData]
UserResponse = BaseResponse[UserData]
SessionResponse = BaseResponse[SessionData]
LogoutResponse = BaseResponse[LogoutData]


class TokenType(str, Enum):
    """Token types for storage and validation."""

    ACCESS = "access_token"
    REFRESH = "refresh_token"


class TokenPair(BaseModel):
    """Pair of access and refresh tokens."""

    access_token: str
    refresh_token: str

    class Config:
        populate_by_name = True

        field_aliases = {
            "access_token": "accessToken",
            "refresh_token": "refreshToken",
        }
