"""Клиент для работы с API Яндекс.Музыки."""

from typing import Optional, TYPE_CHECKING
import asyncio

import yandex_music
from yandex_music import ClientAsync

from src.models import TrackInfo
from src.utils.exceptions import (
    TrackNotFoundError,
    YandexMusicAPIError,
    TimeoutError as YAMTimeoutError,
)
from src.utils.logger import log

if TYPE_CHECKING:
    from src.services.cache import InMemoryCache


class YandexMusicService:
    """Сервис для работы с Яндекс.Музыкой."""

    def __init__(
        self,
        token: Optional[str] = None,
        cache: Optional["InMemoryCache"] = None,
        timeout_seconds: int = 10,
        max_retries: int = 3,
    ) -> None:
        """Инициализация клиента.

        Args:
            token: Опциональный токен для авторизации
            cache: Опциональный кеш для хранения информации о треках
            timeout_seconds: Таймаут для API запросов в секундах
            max_retries: Максимальное количество попыток при ошибке
        """
        self.client = ClientAsync(token)
        self._initialized = False
        self._cache = cache
        self._timeout = timeout_seconds
        self._max_retries = max_retries

    async def _ensure_initialized(self) -> None:
        """Убедиться, что клиент инициализирован."""
        if not self._initialized:
            try:
                await self.client.init()
                self._initialized = True
            except Exception as e:
                log.error(f"Failed to initialize Yandex.Music client: {e}")
                raise YandexMusicAPIError("Failed to connect to Yandex.Music")

    async def get_track_info(self, track_id: str) -> TrackInfo:
        """Получить информацию о треке.

        Args:
            track_id: ID трека

        Returns:
            TrackInfo: Информация о треке

        Raises:
            TrackNotFoundError: Если трек не найден
            YandexMusicAPIError: При ошибке API
            YAMTimeoutError: При превышении таймаута
        """
        # Проверить кеш
        if self._cache:
            cached_track = await self._cache.get(track_id)
            if cached_track:
                log.debug(f"Track {track_id} found in cache")
                return cached_track

        await self._ensure_initialized()

        # Retry logic
        last_exception = None
        for attempt in range(self._max_retries):
            try:
                # Получить трек с timeout
                result = await asyncio.wait_for(
                    self.client.tracks([track_id]),
                    timeout=self._timeout,
                )

                if not result or len(result) == 0:
                    raise TrackNotFoundError(f"Track {track_id} not found")

                track = result[0]

                # Извлечь данные
                artists = [artist.name for artist in track.artists]

                album_title = None
                album_cover = None
                if track.albums and len(track.albums) > 0:
                    album = track.albums[0]
                    album_title = album.title
                    if album.cover_uri:
                        # Заменить %% на размер
                        album_cover = album.cover_uri.replace("%%", "400x400")
                        album_cover = f"https://{album_cover}"

                # Форматировать URL
                if track.albums and len(track.albums) > 0:
                    track_url = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track_id}"
                else:
                    track_url = f"https://music.yandex.ru/track/{track_id}"

                track_info = TrackInfo(
                    track_id=track_id,
                    title=track.title,
                    artists=artists,
                    duration_ms=track.duration_ms,
                    album=album_title,
                    album_cover_url=album_cover,
                    track_url=track_url,
                )

                # Сохранить в кеш
                if self._cache:
                    await self._cache.set(track_id, track_info)
                    log.debug(f"Track {track_id} saved to cache")

                return track_info

            except TrackNotFoundError:
                raise
            except asyncio.TimeoutError as e:
                last_exception = e
                log.warning(
                    f"Timeout fetching track {track_id} (attempt {attempt + 1}/{self._max_retries})"
                )
                if attempt < self._max_retries - 1:
                    # Экспоненциальная задержка
                    delay = 2**attempt
                    await asyncio.sleep(delay)
            except Exception as e:
                last_exception = e
                log.warning(
                    f"Error fetching track {track_id} (attempt {attempt + 1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    # Экспоненциальная задержка
                    delay = 2**attempt
                    await asyncio.sleep(delay)

        # Все попытки исчерпаны
        if isinstance(last_exception, asyncio.TimeoutError):
            log.error(f"Timeout exceeded for track {track_id}")
            raise YAMTimeoutError(f"Request timeout after {self._max_retries} attempts")
        else:
            log.error(f"Failed to fetch track {track_id} after {self._max_retries} attempts")
            raise YandexMusicAPIError(f"Failed to fetch track info: {str(last_exception)}")

    async def close(self) -> None:
        """Закрыть соединение."""
        if self._initialized:
            await self.client.close()
            self._initialized = False
