"""In-memory кеш для хранения информации о треках."""

from typing import Optional
from datetime import datetime, timedelta
from src.models import TrackInfo


class InMemoryCache:
    """In-memory кеш с поддержкой TTL."""

    def __init__(self, ttl_seconds: int = 86400):
        """
        Инициализация кеша.

        Args:
            ttl_seconds: Время жизни записи в секундах (по умолчанию 24 часа)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[TrackInfo, datetime]] = {}

    async def get(self, track_id: str) -> Optional[TrackInfo]:
        """
        Получить информацию о треке из кеша.

        Args:
            track_id: ID трека

        Returns:
            TrackInfo если найден и не истек TTL, иначе None
        """
        if track_id in self._cache:
            track, expiry = self._cache[track_id]
            if datetime.now() < expiry:
                return track
            else:
                # TTL истек, удаляем запись
                del self._cache[track_id]
        return None

    async def set(self, track_id: str, track: TrackInfo) -> None:
        """
        Сохранить информацию о треке в кеш.

        Args:
            track_id: ID трека
            track: Информация о треке
        """
        expiry = datetime.now() + timedelta(seconds=self.ttl_seconds)
        self._cache[track_id] = (track, expiry)

    async def clear(self) -> None:
        """Очистить весь кеш."""
        self._cache.clear()

    async def delete(self, track_id: str) -> bool:
        """
        Удалить конкретный трек из кеша.

        Args:
            track_id: ID трека

        Returns:
            True если трек был найден и удален, иначе False
        """
        if track_id in self._cache:
            del self._cache[track_id]
            return True
        return False

    async def size(self) -> int:
        """
        Получить количество записей в кеше.

        Returns:
            Количество записей
        """
        return len(self._cache)

    async def cleanup_expired(self) -> int:
        """
        Очистить истекшие записи.

        Returns:
            Количество удаленных записей
        """
        now = datetime.now()
        expired_keys = [
            track_id
            for track_id, (_, expiry) in self._cache.items()
            if expiry < now
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)
