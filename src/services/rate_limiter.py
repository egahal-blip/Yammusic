"""Rate limiter для ограничения частоты запросов."""

from collections import defaultdict
from asyncio import Lock
from datetime import datetime, timedelta
from typing import Dict

from src.utils.exceptions import RateLimitError


class InMemoryRateLimiter:
    """In-memory rate limiter для ограничения частоты запросов."""

    # Максимальное количество пользователей для защиты от DoS
    MAX_USERS = 10000

    def __init__(self, max_requests: int = 30, window_seconds: int = 60, max_users: int | None = None):
        """
        Инициализация rate limiter.

        Args:
            max_requests: Максимальное количество запросов
            window_seconds: Временное окно в секундах
            max_users: Максимальное количество пользователей (по умолчанию MAX_USERS)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_users = max_users or self.MAX_USERS
        self._requests: Dict[int, list[datetime]] = defaultdict(list)
        self._lock = Lock()

    async def check_limit(self, user_id: int) -> bool:
        """
        Проверить лимит запросов.

        Args:
            user_id: ID пользователя

        Returns:
            True если лимит не превышен

        Raises:
            RateLimitError: Если превышен лимит запросов или пользователей
        """
        async with self._lock:
            # Проверить лимит пользователей для новых пользователей
            if len(self._requests) >= self.max_users and user_id not in self._requests:
                # Попытаться очистить старых пользователей перед отказом
                await self._cleanup_old_users()

                # Если после очистки все еще превышен лимит
                if len(self._requests) >= self.max_users:
                    raise RateLimitError(
                        "Maximum number of users reached. Please try again later."
                    )

            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)

            # Очистить старые запросы
            self._requests[user_id] = [
                req_time for req_time in self._requests[user_id]
                if req_time > window_start
            ]

            # Проверить лимит
            if len(self._requests[user_id]) >= self.max_requests:
                raise RateLimitError(
                    f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds} seconds"
                )

            # Добавить текущий запрос
            self._requests[user_id].append(now)
            return True

    async def get_remaining_requests(self, user_id: int) -> int:
        """
        Получить количество оставшихся запросов.

        Args:
            user_id: ID пользователя

        Returns:
            Количество оставшихся запросов
        """
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)

            # Очистить старые запросы
            self._requests[user_id] = [
                req_time for req_time in self._requests[user_id]
                if req_time > window_start
            ]

            return max(0, self.max_requests - len(self._requests[user_id]))

    async def reset_user(self, user_id: int) -> None:
        """
        Сбросить счетчик запросов для пользователя.

        Args:
            user_id: ID пользователя
        """
        async with self._lock:
            if user_id in self._requests:
                self._requests[user_id].clear()

    async def _cleanup_old_users(self) -> None:
        """Удалить неактивных пользователей для освобождения памяти."""
        now = datetime.now()
        # Удаляем пользователей, не активных в течение 10 окон
        window_start = now - timedelta(seconds=self.window_seconds * 10)

        to_delete = [
            user_id for user_id, requests in self._requests.items()
            if not requests or requests[-1] < window_start
        ]

        for user_id in to_delete:
            del self._requests[user_id]

        if to_delete:
            log_debug = __import__('src.utils.logger', fromlist=['log']).log
            log_debug.debug(f"[RATE_LIMITER] Cleaned up {len(to_delete)} inactive users")
