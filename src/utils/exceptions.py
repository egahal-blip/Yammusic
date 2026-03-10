"""Кастомные исключения приложения."""


class YAMBotError(Exception):
    """Базовое исключение приложения."""
    pass


class InvalidURLError(YAMBotError):
    """Неверный формат URL."""
    pass


class TrackNotFoundError(YAMBotError):
    """Трек не найден."""
    pass


class YandexMusicAPIError(YAMBotError):
    """Ошибка API Яндекс.Музыки."""
    pass


class RateLimitError(YAMBotError):
    """Превышен лимит запросов."""
    pass


class TimeoutError(YAMBotError):
    """Превышено время ожидания."""
    pass
