import pytest
from src.config import Settings, get_settings


def test_get_settings_singleton():
    """Тест singleton паттерна"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_values():
    """Тест значений настроек"""
    settings = get_settings()
    assert settings.telegram_bot_token
    assert settings.log_level == "INFO"
    assert settings.rate_limit_per_minute == 30
    assert settings.cache_ttl_seconds == 86400
    assert settings.api_timeout_seconds == 10
    assert settings.api_max_retries == 3
    assert settings.redis_host == "localhost"
    assert settings.redis_port == 6379
    assert settings.redis_db == 0
