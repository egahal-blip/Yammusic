"""Парсер ссылок Яндекс.Музыки."""

import re
from dataclasses import dataclass
from typing import Optional

from src.utils.exceptions import InvalidURLError
from src.utils.validators import validate_track_id, validate_album_id


@dataclass
class ParsedURL:
    """Результат парсинга URL."""

    track_id: str
    album_id: Optional[str] = None
    original_url: str = ""


class YandexMusicURLParser:
    """Парсер ссылок Яндекс.Музыки."""

    # Поддерживаемые форматы URL
    PATTERNS = [
        # https://music.yandex.ru/album/{album_id}/track/{track_id}
        r"https?://music\.yandex\.ru/album/(\d+)/track/(\d+)",
        # https://music.yandex.ru/track/{track_id}
        r"https?://music\.yandex\.ru/track/(\d+)",
    ]

    def __init__(self) -> None:
        """Инициализация парсера."""
        self._compiled_patterns = [re.compile(p) for p in self.PATTERNS]

    def parse(self, url: str) -> ParsedURL:
        """Распарсить URL и извлечь track_id.

        Args:
            url: URL ссылки на трек

        Returns:
            ParsedURL: Объект с извлеченными данными

        Raises:
            InvalidURLError: Если URL не соответствует поддерживаемым форматам
        """
        url = url.strip()

        # Удалить query параметры (utm_source и т.д.)
        url = url.split('?')[0]
        url = url.split('#')[0]

        # Проверить каждый паттерн
        for pattern in self._compiled_patterns:
            match = pattern.fullmatch(url)
            if match:
                groups = match.groups()

                # Первый формат: album/track
                if len(groups) == 2:
                    album_id, track_id = groups

                    # Валидировать IDs
                    if not validate_album_id(album_id) or not validate_track_id(track_id):
                        raise InvalidURLError(f"Invalid album or track ID in URL: {url}")

                    return ParsedURL(
                        track_id=track_id,
                        album_id=album_id,
                        original_url=url
                    )
                # Второй формат: track only
                elif len(groups) == 1:
                    track_id = groups[0]

                    # Валидировать track_id
                    if not validate_track_id(track_id):
                        raise InvalidURLError(f"Invalid track ID in URL: {url}")

                    return ParsedURL(
                        track_id=track_id,
                        original_url=url
                    )

        # Если ни один паттерн не подошел
        raise InvalidURLError(f"Invalid Yandex.Music URL: {url}")

    def is_valid_url(self, url: str) -> bool:
        """Проверить валидность URL.

        Args:
            url: URL для проверки

        Returns:
            True если URL валидный, иначе False
        """
        try:
            self.parse(url)
            return True
        except InvalidURLError:
            return False
