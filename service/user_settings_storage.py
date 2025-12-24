from typing import Optional, Dict, Tuple, List
from threading import Lock
from pydantic import BaseModel
from models import MARKETS_TYPE, TRADING_TYPE, LANGUAGES_TYPE


class UserSettings(BaseModel):
    lang: LANGUAGES_TYPE = "ru"
    deposit: float = 10000
    risk: Tuple[float, bool] = (1, True)
    currency: str = "USDT"
    market: MARKETS_TYPE = "crypto"
    tp_ratio: List[float] = [3]
    split_values: Optional[List[float]] = None
    trading_style: Optional[str] = None
    round_count: Optional[int] = None
    day_risk: Optional[Tuple[float, bool]] = None
    is_updating_deposit: bool = False
    trading_type: TRADING_TYPE = "margin"
    is_from_deposit: bool = False


class UserSettingsStorage:
    def __init__(self) -> None:
        self._storage: Dict[int, UserSettings] = {}
        self._lock = Lock()

    def set(self, user_id: int, settings: UserSettings) -> None:
        with self._lock:
            self._storage[user_id] = settings

    def get(self, user_id: int) -> Optional[UserSettings]:
        with self._lock:
            return self._storage.get(user_id)

    def _get_or_create_unlocked(self, user_id: int) -> UserSettings:
        """Internal method without lock - assumes lock is already held."""
        if user_id not in self._storage:
            self._storage[user_id] = UserSettings()
        return self._storage[user_id]

    def get_or_create(self, user_id: int) -> UserSettings:
        with self._lock:
            return self._get_or_create_unlocked(user_id)

    def get_lang(self, user_id: int) -> LANGUAGES_TYPE:
        settings = self.get_or_create(user_id)
        return settings.lang

    def set_lang(self, user_id: int, lang: LANGUAGES_TYPE) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.lang = lang
            self._storage[user_id] = settings

    def get_deposit(self, user_id: int) -> float:
        settings = self.get_or_create(user_id)
        return settings.deposit

    def set_deposit(self, user_id: int, deposit: float) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.deposit = deposit
            self._storage[user_id] = settings

    def get_risk(self, user_id: int) -> Tuple[float, bool]:
        settings = self.get_or_create(user_id)
        return settings.risk

    def set_risk(self, user_id: int, risk: Tuple[float, bool]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.risk = risk
            self._storage[user_id] = settings

    def get_currency(self, user_id: int) -> str:
        settings = self.get_or_create(user_id)
        return settings.currency

    def set_currency(self, user_id: int, currency: str) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.currency = currency
            self._storage[user_id] = settings

    def get_market(self, user_id: int) -> MARKETS_TYPE:
        settings = self.get_or_create(user_id)
        return settings.market

    def set_market(self, user_id: int, market: MARKETS_TYPE) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.market = market
            self._storage[user_id] = settings

    def get_tp_ratio(self, user_id: int) -> List[float]:
        settings = self.get_or_create(user_id)
        return settings.tp_ratio

    def set_tp_ratio(self, user_id: int, tp_ratio: List[float]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.tp_ratio = tp_ratio
            self._storage[user_id] = settings

    def get_split_values(self, user_id: int) -> Optional[List[float]]:
        settings = self.get_or_create(user_id)
        return settings.split_values

    def set_split_values(self, user_id: int, split_values: Optional[List[float]]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.split_values = split_values
            self._storage[user_id] = settings

    def get_trading_style(self, user_id: int) -> Optional[str]:
        settings = self.get_or_create(user_id)
        return settings.trading_style

    def set_trading_style(self, user_id: int, trading_style: Optional[str]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.trading_style = trading_style
            self._storage[user_id] = settings

    def get_round_count(self, user_id: int) -> Optional[int]:
        settings = self.get_or_create(user_id)
        return settings.round_count

    def set_round_count(self, user_id: int, round_count: Optional[int]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.round_count = round_count
            self._storage[user_id] = settings

    def get_day_risk(self, user_id: int) -> Optional[Tuple[float, bool]]:
        settings = self.get_or_create(user_id)
        return settings.day_risk

    def set_day_risk(self, user_id: int, day_risk: Optional[Tuple[float, bool]]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.day_risk = day_risk
            self._storage[user_id] = settings

    def get_is_updating_deposit(self, user_id: int) -> bool:
        settings = self.get_or_create(user_id)
        return settings.is_updating_deposit

    def set_is_updating_deposit(self, user_id: int, is_updating: bool) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.is_updating_deposit = is_updating
            self._storage[user_id] = settings

    def get_trading_type(self, user_id: int) -> TRADING_TYPE:
        settings = self.get_or_create(user_id)
        return settings.trading_type

    def set_trading_type(self, user_id: int, trading_type: TRADING_TYPE) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.trading_type = trading_type
            self._storage[user_id] = settings

    def get_is_from_deposit(self, user_id: int) -> bool:
        settings = self.get_or_create(user_id)
        return settings.is_from_deposit

    def set_is_from_deposit(self, user_id: int, is_from_deposit: bool) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.is_from_deposit = is_from_deposit
            self._storage[user_id] = settings

    def update(self, user_id: int, **kwargs) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings_dict = settings.model_dump()

            for key, value in kwargs.items():
                if key in settings_dict:
                    settings_dict[key] = value

            self._storage[user_id] = UserSettings(**settings_dict)

    def remove(self, user_id: int) -> None:
        with self._lock:
            self._storage.pop(user_id, None)

    def clear(self) -> None:
        """Clear all stored settings."""
        with self._lock:
            self._storage.clear()

    def has_user(self, user_id: int) -> bool:
        with self._lock:
            return user_id in self._storage


user_settings_storage = UserSettingsStorage()
