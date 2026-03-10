import pytest
from src.models import TrackInfo, UserRequest


def test_track_info_duration_validation():
    """Тест валидации длительности"""
    with pytest.raises(ValueError, match="Duration must be positive"):
        TrackInfo(
            track_id="123",
            title="Test",
            artists=["Artist"],
            duration_ms=-100,
            track_url="https://example.com"
        )


def test_track_info_duration_formatted():
    """Тест форматирования длительности"""
    track = TrackInfo(
        track_id="123",
        title="Test",
        artists=["Artist"],
        duration_ms=180000,  # 3 минуты
        track_url="https://example.com"
    )
    assert track.duration_formatted == "03:00"


def test_track_info_duration_formatted_with_seconds():
    """Тест форматирования длительности с секундами"""
    track = TrackInfo(
        track_id="123",
        title="Test",
        artists=["Artist"],
        duration_ms=125000,  # 2:05
        track_url="https://example.com"
    )
    assert track.duration_formatted == "02:05"


def test_track_info_artists_formatted():
    """Тест форматирования артистов"""
    track = TrackInfo(
        track_id="123",
        title="Test",
        artists=["Artist1", "Artist2", "Artist3"],
        duration_ms=180000,
        track_url="https://example.com"
    )
    assert track.artists_formatted == "Artist1, Artist2, Artist3"


def test_track_info_with_album():
    """Тест трека с альбомом"""
    track = TrackInfo(
        track_id="123",
        title="Test Track",
        artists=["Test Artist"],
        duration_ms=200000,
        album="Test Album",
        album_cover_url="https://example.com/cover.jpg",
        track_url="https://music.yandex.ru/album/1/track/123"
    )
    assert track.album == "Test Album"
    assert track.album_cover_url == "https://example.com/cover.jpg"


def test_track_info_without_album():
    """Тест трека без альбома"""
    track = TrackInfo(
        track_id="123",
        title="Test Track",
        artists=["Test Artist"],
        duration_ms=200000,
        track_url="https://music.yandex.ru/track/123"
    )
    assert track.album is None
    assert track.album_cover_url is None


def test_user_request_creation():
    """Тест создания запроса пользователя"""
    request = UserRequest(
        user_id=12345,
        username="testuser",
        track_url="https://music.yandex.ru/track/123",
        success=True
    )
    assert request.user_id == 12345
    assert request.username == "testuser"
    assert request.track_url == "https://music.yandex.ru/track/123"
    assert request.success is True
    assert request.timestamp is not None


def test_user_request_with_error():
    """Тест запроса с ошибкой"""
    request = UserRequest(
        user_id=12345,
        track_url="https://invalid.url",
        success=False,
        error_message="Invalid URL"
    )
    assert request.success is False
    assert request.error_message == "Invalid URL"
