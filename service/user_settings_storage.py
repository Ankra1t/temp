from typing import Optional, Dict, Tuple, List
from threading import Lock
from pydantic import BaseModel
from models import MARKETS_TYPE, TRADING_TYPE, LANGUAGES_TYPE, Exchange


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
    exchange: Optional[Tuple[Optional[str], Optional[float]]] = None
    stop: Optional[str] = None
    style_change: bool = False
    atr_settings: Tuple[bool, str] = (True, '1h+5')


class UserSettingsStorage:
    def __init__(self) -> None:
        self._storage: Dict[int, UserSettings] = {}
        self._lock = Lock()
        # Глобальные данные из data.py
        self._exchanges: List[Exchange] = []
        self._send_settings: Dict[str, Optional[str]] = {}

    def _get_or_create_unlocked(self, user_id: int) -> UserSettings:
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

    def set_deposit(self, user_id: int, deposit: float) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.deposit = deposit
            self._storage[user_id] = settings

    def set_risk(self, user_id: int, risk: Tuple[float, bool]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.risk = risk
            self._storage[user_id] = settings

    def set_currency(self, user_id: int, currency: str) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.currency = currency
            self._storage[user_id] = settings

    def set_market(self, user_id: int, market: MARKETS_TYPE) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.market = market
            self._storage[user_id] = settings

    def set_tp_ratio(self, user_id: int, tp_ratio: List[float]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.tp_ratio = tp_ratio
            self._storage[user_id] = settings

    def set_split_values(self, user_id: int, split_values: Optional[List[float]]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.split_values = split_values
            self._storage[user_id] = settings

    def set_trading_style(self, user_id: int, trading_style: Optional[str]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.trading_style = trading_style
            self._storage[user_id] = settings

    def set_round_count(self, user_id: int, round_count: Optional[int]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.round_count = round_count
            self._storage[user_id] = settings

    def set_day_risk(self, user_id: int, day_risk: Optional[Tuple[float, bool]]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.day_risk = day_risk
            self._storage[user_id] = settings

    def set_is_updating_deposit(self, user_id: int, is_updating: bool) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.is_updating_deposit = is_updating
            self._storage[user_id] = settings

    def set_trading_type(self, user_id: int, trading_type: TRADING_TYPE) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.trading_type = trading_type
            self._storage[user_id] = settings

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

    def get_user_exchange(self, user_id: int) -> Optional[Tuple[str, float]]:
        settings = self.get_or_create(user_id)
        exchange = settings.exchange
        if exchange is None or exchange[0] is None or exchange[1] is None:
            return None
        return (exchange[0], exchange[1])

    def set_user_exchange(self, user_id: int, value: Tuple[Optional[str], Optional[float]]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.exchange = value
            self._storage[user_id] = settings

    def get_user_stop(self, user_id: int) -> Optional[str]:
        settings = self.get_or_create(user_id)
        return settings.stop

    def set_user_stop(self, user_id: int, stop: str) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.stop = stop
            self._storage[user_id] = settings

    def get_style_change(self, user_id: int) -> bool:
        settings = self.get_or_create(user_id)
        return settings.style_change

    def switch_style_change(self, user_id: int) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.style_change = not settings.style_change
            self._storage[user_id] = settings

    def get_user_atr_settings(self, user_id: int) -> Tuple[bool, str]:
        settings = self.get_or_create(user_id)
        return settings.atr_settings

    def set_user_atr_settings(self, user_id: int, value: Tuple[bool, str]) -> None:
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)
            settings.atr_settings = value
            self._storage[user_id] = settings

    def set_exchanges(self, exchanges: List[Exchange]) -> None:
        with self._lock:
            self._exchanges = exchanges

    def get_exchanges(self) -> List[Exchange]:
        return self._exchanges

    def get_exchange_by_name(self, name: str) -> Optional[Exchange]:
        for exchange in self._exchanges:
            if exchange.name == name:
                return exchange
        return None

    def get_send_settings(self, name: str) -> Optional[str]:
        with self._lock:
            return self._send_settings.get(name)

    def update_send_settings(self, name: str, value: Optional[str]) -> None:
        with self._lock:
            self._send_settings[name] = value


user_settings_storage = UserSettingsStorage()
