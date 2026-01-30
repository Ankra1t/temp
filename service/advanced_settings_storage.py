from typing import Optional, Dict
from threading import Lock
from pydantic import BaseModel
from models import AdvancedSettings


class AdvancedSettingsData(BaseModel):
    autoOpen: bool = False
    autoStop: bool = False
    autoTake: Optional[float] = None
    trailingStop: Optional[float] = None
    cancelMinutes: Optional[float] = None


class AdvancedSettingsStorage:
    """Сервис для хранения продвинутых настроек расчётов в памяти"""

    def __init__(self) -> None:
        self._storage: Dict[int, AdvancedSettingsData] = {}
        self._lock = Lock()

    def _get_or_create_unlocked(self, user_id: int) -> AdvancedSettingsData:
        if user_id not in self._storage:
            self._storage[user_id] = AdvancedSettingsData()
        return self._storage[user_id]

    def get_or_create(self, user_id: int) -> AdvancedSettingsData:
        with self._lock:
            return self._get_or_create_unlocked(user_id)

    def get_advanced(self, user_id: int) -> Optional[AdvancedSettings]:
        """Получить AdvancedSettings для API (с userId)"""
        settings = self.get_or_create(user_id)
        return AdvancedSettings(
            userId=user_id,
            autoOpen=settings.autoOpen,
            autoStop=settings.autoStop,
            autoTake=settings.autoTake,
            trailingStop=settings.trailingStop,
            cancelMinutes=settings.cancelMinutes,
        )

    def update_advanced(
        self,
        user_id: int,
        autoOpen: Optional[bool] = None,
        autoStop: Optional[bool] = None,
        autoTake: Optional[float] = None,
        trailingStop: Optional[float] = None,
        cancelMinutes: Optional[float] = None,
    ) -> Optional[AdvancedSettings]:
        """Обновить AdvancedSettings и вернуть обновлённые"""
        with self._lock:
            settings = self._get_or_create_unlocked(user_id)

            if autoOpen is not None:
                settings.autoOpen = autoOpen
            if autoStop is not None:
                settings.autoStop = autoStop
            if autoTake is not None:
                settings.autoTake = autoTake
            if trailingStop is not None:
                settings.trailingStop = trailingStop
            if cancelMinutes is not None:
                settings.cancelMinutes = cancelMinutes

            self._storage[user_id] = settings

            return AdvancedSettings(
                userId=user_id,
                autoOpen=settings.autoOpen,
                autoStop=settings.autoStop,
                autoTake=settings.autoTake,
                trailingStop=settings.trailingStop,
                cancelMinutes=settings.cancelMinutes,
            )

    def remove(self, user_id: int) -> None:
        """Удалить данные пользователя"""
        with self._lock:
            self._storage.pop(user_id, None)


# Глобальный экземпляр сервиса
advanced_settings_storage = AdvancedSettingsStorage()
