from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Конфигурация приложения"""

    # Telegram Bot
    telegram_bot_token: str
    telegram_proxy_url: str | None = None  # Прокси для подключения к Telegram (опционально)
    allowed_user_ids: list[int] = []  # Список разрешенных user_id для админ-команд

    # Yandex.Music
    yandex_music_token: str | None = None

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Application
    log_level: str = "INFO"
    rate_limit_per_minute: int = 30
    cache_ttl_seconds: int = 86400

    # API Settings
    api_timeout_seconds: int = 10
    api_max_retries: int = 3

    # Webhook Settings
    use_webhook: bool = False  # False = polling, True = webhook
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8443
    webhook_path: str = "/telegram-webhook"
    webhook_url: str = ""  # Полный URL: https://domain.com/telegram-webhook
    webhook_secret_token: str = ""  # Секретный токен для проверки webhook запросов

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Получить Singleton экземпляр настроек"""
    return Settings()
