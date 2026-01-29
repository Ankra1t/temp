from typing import Dict
from threading import Lock


class UserService:
    """Сервис для хранения пользовательских данных в памяти"""

    def __init__(self) -> None:
        self._lesson_counts: Dict[int, int] = {}
        self._lock = Lock()

    def get_lesson_count(self, user_id: int) -> int:
        """Получить количество пройденных уроков пользователя"""
        with self._lock:
            return self._lesson_counts.get(user_id, 1)

    def set_lesson_count(self, user_id: int, count: int) -> None:
        """Установить количество пройденных уроков"""
        with self._lock:
            self._lesson_counts[user_id] = count

    def add_lesson_count(self, user_id: int) -> None:
        """Увеличить количество пройденных уроков на 1"""
        with self._lock:
            current = self._lesson_counts.get(user_id, 1)
            self._lesson_counts[user_id] = current + 1

    def remove(self, user_id: int) -> None:
        """Удалить данные пользователя"""
        with self._lock:
            self._lesson_counts.pop(user_id, None)


# Глобальный экземпляр сервиса
user_service = UserService()
