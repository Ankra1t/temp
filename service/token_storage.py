from typing import Optional, Dict
from threading import Lock
from datetime import datetime, timedelta

from service.base import TokenPair


class TokenStorage:
    def __init__(self) -> None:
        self._storage: Dict[int, TokenPair] = {}
        self._lock = Lock()
        self._expires_at: Dict[int, datetime] = {}

    def set(self, user_id: int, tokens: TokenPair, ttl_seconds: int = 3600) -> None:
        with self._lock:
            self._storage[user_id] = tokens
            self._expires_at[user_id] = datetime.now() + \
                timedelta(seconds=ttl_seconds)

    def get(self, user_id: int) -> Optional[TokenPair]:
        with self._lock:
            return self._storage.get(user_id)

    def get_access_token(self, user_id: int) -> Optional[str]:
        tokens = self.get(user_id)
        return tokens.access_token if tokens else None

    def get_refresh_token(self, user_id: int) -> Optional[str]:
        tokens = self.get(user_id)
        return tokens.refresh_token if tokens else None

    def update(self, user_id: int, **kwargs: str) -> None:
        with self._lock:
            if user_id not in self._storage:
                return

            tokens = self._storage[user_id]
            token_dict = tokens.model_dump()

            for key, value in kwargs.items():
                if key in token_dict:
                    token_dict[key] = value

            self._storage[user_id] = TokenPair(**token_dict)

    def is_expired(self, user_id: int, buffer_seconds: int = 60) -> bool:
        with self._lock:
            if user_id not in self._expires_at:
                return True

            expiration = self._expires_at[user_id]
            return datetime.now() >= (expiration - timedelta(seconds=buffer_seconds))

    def remove(self, user_id: int) -> None:
        with self._lock:
            self._storage.pop(user_id, None)
            self._expires_at.pop(user_id, None)

    def clear(self) -> None:
        with self._lock:
            self._storage.clear()
            self._expires_at.clear()

    def has_user(self, user_id: int) -> bool:
        with self._lock:
            return user_id in self._storage


token_storage = TokenStorage()
