"""Тесты для клиента Яндекс.Музыки."""

import pytest

from src.services.yandex_music import YandexMusicService
from src.utils.exceptions import TrackNotFoundError, YandexMusicAPIError
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def service() -> YandexMusicService:
    """Создать экземпляр сервиса."""
    return YandexMusicService()


@pytest.mark.asyncio
async def test_service_initialization(service: YandexMusicService) -> None:
    """Тест инициализации сервиса."""
    assert service is not None
    assert service._initialized is False


@pytest.mark.asyncio
async def test_get_track_info_success(service: YandexMusicService) -> None:
    """Тест успешного получения информации о треке."""
    # Mock трек
    mock_artist = MagicMock()
    mock_artist.name = "Test Artist"

    mock_album = MagicMock()
    mock_album.id = 123
    mock_album.title = "Test Album"
    mock_album.cover_uri = "covers/%%"

    mock_track = MagicMock()
    mock_track.title = "Test Track"
    mock_track.duration_ms = 180000
    mock_track.artists = [mock_artist]
    mock_track.albums = [mock_album]

    # Mock client
    mock_client = AsyncMock()
    mock_client.tracks = AsyncMock(return_value=[mock_track])

    service.client = mock_client
    service._initialized = True

    # Test
    result = await service.get_track_info("12345")

    assert result.title == "Test Track"
    assert result.artists == ["Test Artist"]
    assert result.duration_formatted == "03:00"
    assert result.album == "Test Album"
    assert result.track_id == "12345"


@pytest.mark.asyncio
async def test_get_track_info_not_found(service: YandexMusicService) -> None:
    """Тест случая, когда трек не найден."""
    # Mock client returns empty list
    mock_client = AsyncMock()
    mock_client.tracks = AsyncMock(return_value=[])

    service.client = mock_client
    service._initialized = True

    # Test
    with pytest.raises(TrackNotFoundError):
        await service.get_track_info("99999")


@pytest.mark.asyncio
async def test_get_track_info_api_error(service: YandexMusicService) -> None:
    """Тест обработки ошибки API."""
    # Mock client raises exception
    mock_client = AsyncMock()
    mock_client.init = AsyncMock(side_effect=Exception("Connection error"))

    service.client = mock_client

    # Test
    with pytest.raises(YandexMusicAPIError):
        await service.get_track_info("12345")


@pytest.mark.asyncio
async def test_close_connection(service: YandexMusicService) -> None:
    """Тест закрытия соединения."""
    mock_client = AsyncMock()
    mock_client.close = AsyncMock()

    service.client = mock_client
    service._initialized = True

    await service.close()

    assert service._initialized is False
    mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_track_without_album(service: YandexMusicService) -> None:
    """Тест трека без альбома."""
    mock_artist = MagicMock()
    mock_artist.name = "Solo Artist"

    mock_track = MagicMock()
    mock_track.title = "Single Track"
    mock_track.duration_ms = 210000
    mock_track.artists = [mock_artist]
    mock_track.albums = []

    mock_client = AsyncMock()
    mock_client.tracks = AsyncMock(return_value=[mock_track])

    service.client = mock_client
    service._initialized = True

    result = await service.get_track_info("12345")

    assert result.album is None
    assert result.album_cover_url is None
    assert "track/12345" in result.track_url
