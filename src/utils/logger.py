from loguru import logger
import sys
import re
from pathlib import Path


def setup_logger(log_level: str = "INFO") -> None:
    """Настройка логирования"""

    # Удалить дефолтный handler
    logger.remove()

    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger.add(
        logs_dir / "bot_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        filter=SecretFilter(),
    )


# Инициализация логгера
log = logger


def sanitize_for_log(text: str | None, max_length: int = 50) -> str:
    """Очистить текст для логирования, удалив потенциальные секреты.

    Args:
        text: Текст для очистки
        max_length: Максимальная длина результата

    Returns:
        Очищенный текст
    """
    if not text:
        return ""

    # Удалить паттерны, похожие на токены (длинные alphanumeric строки)
    text = re.sub(r'\b[a-zA-Z0-9_-]{30,}\b', '[REDACTED]', text)

    # Удалить паттерны токенов Telegram (число:строка)
    text = re.sub(r'\b\d{8,}:[A-Za-z0-9_-]{30,}\b', '[TOKEN_REDACTED]', text)

    # Удалить паттерны типа "token=xxx", "password=xxx"
    text = re.sub(
        r'(token|password|secret|api_key|auth)["\']?\s*[:=]\s*["\']?[^"\']+\b',
        r'\1=[REDACTED]',
        text,
        flags=re.IGNORECASE
    )

    # Обрезать
    return text[:max_length]


class SecretFilter:
    """Фильтр для автоматического скрытия секретов в логах."""

    def __call__(self, record: dict) -> bool:
        """Обработать запись лога.

        Args:
            record: Запись лога

        Returns:
            True для записи лога
        """
        record["message"] = self._sanitize(record["message"])
        return True

    def _sanitize(self, message: str) -> str:
        """Маскировать секреты в сообщении.

        Args:
            message: Сообщение для очистки

        Returns:
            Очищенное сообщение
        """
        # Маскировать токены, пароли и т.д.
        message = re.sub(
            r'(token|password|secret|api_key|auth)["\']?\s*[:=]\s*["\']?[^"\']+',
            r'\1=[REDACTED]',
            message,
            flags=re.IGNORECASE
        )
        # Маскировать длинные alphanumeric строки
        message = re.sub(r'\b[a-zA-Z0-9_-]{30,}\b', '[REDACTED]', message)
        return message
