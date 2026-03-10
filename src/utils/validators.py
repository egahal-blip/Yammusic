"""Валидаторы данных приложения."""

import re
from typing import Optional

# Максимальная длина пользовательского ввода (для защиты от DoS)
MAX_MESSAGE_LENGTH = 1000
MAX_URL_LENGTH = 2048


def validate_track_id(track_id: str) -> bool:
    """Валидировать ID трека.

    Args:
        track_id: ID трека для проверки

    Returns:
        True если ID валиден, иначе False
    """
    if not track_id:
        return False

    # ID трека должен быть числом
    if not track_id.isdigit():
        return False

    # Проверить длину (ID обычно от 1 до 20 цифр)
    if not 1 <= len(track_id) <= 20:
        return False

    return True


def validate_album_id(album_id: str) -> bool:
    """Валидировать ID альбома.

    Args:
        album_id: ID альбома для проверки

    Returns:
        True если ID валиден, иначе False
    """
    if not album_id:
        return False

    # ID альбома должен быть числом
    if not album_id.isdigit():
        return False

    # Проверить длину
    if not 1 <= len(album_id) <= 20:
        return False

    return True


def sanitize_track_id(track_id: str) -> Optional[str]:
    """Очистить ID трека от лишних символов.

    Args:
        track_id: ID трека для очистки

    Returns:
        Очищенный ID или None если невалиден
    """
    if not track_id:
        return None

    # Удалить все кроме цифр
    cleaned = re.sub(r"[^0-9]", "", track_id)

    if not cleaned:
        return None

    # Проверить валидность
    if validate_track_id(cleaned):
        return cleaned

    return None


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """Очистить пользовательский ввод.

    Args:
        text: Пользовательский текст
        max_length: Максимальная длина

    Returns:
        Очищенный текст
    """
    if not text:
        return ""

    # Обрезать до максимальной длины
    cleaned = text[:max_length]

    # Удалить null байты и управляющие символы (кроме \n, \r, \t)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    return cleaned.strip()


def validate_url_format(url: str) -> bool:
    """Проверить базовый формат URL.

    Args:
        url: URL для проверки

    Returns:
        True если формат валиден, иначе False
    """
    if not url:
        return False

    # Базовая проверка формата URL
    url_pattern = re.compile(
        r"^https?://"  # http:// или https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return bool(url_pattern.match(url))


def extract_numeric_id(text: str) -> Optional[str]:
    """Извлечь числовой ID из текста.

    Args:
        text: Текст для поиска

    Returns:
        Найденный ID или None
    """
    if not text:
        return None

    # Найти все числа в тексте
    numbers = re.findall(r"\d+", text)

    # Вернуть первое найденное число
    if numbers:
        return numbers[0]

    return None


def validate_message_length(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> bool:
    """Проверить длину сообщения.

    Args:
        text: Текст для проверки
        max_length: Максимальная длина

    Returns:
        True если длина допустима, иначе False
    """
    if not text:
        return False
    return len(text) <= max_length


def validate_url_length(url: str, max_length: int = MAX_URL_LENGTH) -> bool:
    """Проверить длину URL.

    Args:
        url: URL для проверки
        max_length: Максимальная длина

    Returns:
        True если длина допустима, иначе False
    """
    if not url:
        return False
    return len(url) <= max_length
