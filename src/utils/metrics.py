"""Метрики приложения."""

from time import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """Метрики запроса."""

    count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0

    def update(self, success: bool, duration: float) -> None:
        """Обновить метрики.

        Args:
            success: Успешность запроса
            duration: Время выполнения в секундах
        """
        self.count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        # Обновить среднее время
        self.total_time += duration
        self.avg_time = self.total_time / self.count

    def get_success_rate(self) -> float:
        """Получить процент успешных запросов."""
        if self.count == 0:
            return 0.0
        return (self.success_count / self.count) * 100


class MetricsCollector:
    """Сборщик метрик приложения."""

    def __init__(self) -> None:
        """Инициализация сборщика метрик."""
        self._track_requests: RequestMetrics = RequestMetrics()
        self._user_requests: Dict[int, RequestMetrics] = defaultdict(RequestMetrics)
        self._error_types: Dict[str, int] = defaultdict(int)
        self._start_time: float = time()

    def record_request(
        self,
        user_id: int,
        success: bool,
        duration: float,
        error_type: Optional[str] = None,
    ) -> None:
        """Записать метрики запроса.

        Args:
            user_id: ID пользователя
            success: Успешность запроса
            duration: Время выполнения в секундах
            error_type: Тип ошибки (если была)
        """
        # Общие метрики
        self._track_requests.update(success, duration)

        # Метрики пользователя
        self._user_requests[user_id].update(success, duration)

        # Типы ошибок
        if not success and error_type:
            self._error_types[error_type] += 1

    def get_summary(self) -> dict:
        """Получить сводку метрик."""
        uptime = time() - self._start_time

        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "total_requests": self._track_requests.count,
            "successful_requests": self._track_requests.success_count,
            "failed_requests": self._track_requests.error_count,
            "success_rate": self._track_requests.get_success_rate(),
            "avg_response_time": self._track_requests.avg_time,
            "error_types": dict(self._error_types),
            "unique_users": len(self._user_requests),
        }

    def get_user_metrics(self, user_id: int) -> dict:
        """Получить метрики пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Словарь с метриками пользователя
        """
        if user_id not in self._user_requests:
            return {
                "user_id": user_id,
                "requests": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
            }

        metrics = self._user_requests[user_id]

        return {
            "user_id": user_id,
            "requests": metrics.count,
            "successful_requests": metrics.success_count,
            "failed_requests": metrics.error_count,
            "success_rate": metrics.get_success_rate(),
            "avg_response_time": metrics.avg_time,
        }

    def reset(self) -> None:
        """Сбросить все метрики."""
        self._track_requests = RequestMetrics()
        self._user_requests.clear()
        self._error_types.clear()
        self._start_time = time()

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Форматировать время работы.

        Args:
            seconds: Секунды

        Returns:
            Отформатированная строка
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# Глобальный экземпляр сборщика метрик
metrics = MetricsCollector()
