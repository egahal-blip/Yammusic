"""Тесты для форматтера ответов."""

import pytest

from src.services.formatter import ResponseFormatter
from src.models import TrackInfo


@pytest.fixture
def formatter() -> ResponseFormatter:
    """Создать экземпляр форматтера."""
    return ResponseFormatter()


@pytest.fixture
def sample_track() -> TrackInfo:
    """Создать тестовый трек."""
    return TrackInfo(
        track_id="12345",
        title="Test Song",
        artists=["Artist One", "Artist Two"],
        duration_ms=180000,  # 3:00
        album="Test Album",
        album_cover_url="https://example.com/cover.jpg",
        track_url="https://music.yandex.ru/album/123/track/456",
    )


def test_format_track_info_basic(formatter: ResponseFormatter, sample_track: TrackInfo) -> None:
    """Тест базового форматирования информации о треке."""
    result = formatter.format_track_info(sample_track)

    assert "🎵" in result
    assert "Test Song" in result
    assert "Artist One, Artist Two" in result
    assert "03:00" in result
    assert "Test Album" in result
    assert "https://music.yandex.ru/album/123/track/456" in result


def test_format_track_info_without_album(formatter: ResponseFormatter) -> None:
    """Тест форматирования трека без альбома."""
    track = TrackInfo(
        track_id="123",
        title="Single",
        artists=["Solo Artist"],
        duration_ms=210000,
        album=None,
        album_cover_url=None,
        track_url="https://music.yandex.ru/track/123",
    )

    result = formatter.format_track_info(track)

    assert "Single" in result
    assert "Solo Artist" in result
    assert "03:30" in result
    # Альбом не должен отображаться
    assert "Альбом:" not in result


def test_format_error_invalid_url(formatter: ResponseFormatter) -> None:
    """Тест форматирования ошибки неверного URL."""
    result = formatter.format_error("invalid_url")

    assert "❌" in result
    assert "Неверный формат ссылки" in result
    assert "Пример:" in result


def test_format_error_track_not_found(formatter: ResponseFormatter) -> None:
    """Тест форматирования ошибки 'трек не найден'."""
    result = formatter.format_error("track_not_found")

    assert "🔍" in result
    assert "Трек не найден" in result


def test_format_error_with_details(formatter: ResponseFormatter) -> None:
    """Тест форматирования ошибки с деталями."""
    result = formatter.format_error("api_error", "Connection timeout")

    assert "⚠️" in result
    assert "Connection timeout" in result


def test_format_error_unknown(formatter: ResponseFormatter) -> None:
    """Тест форматирования неизвестной ошибки."""
    result = formatter.format_error("nonexistent_type")

    assert "❌" in result
    assert "Произошла ошибка" in result


def test_escape_html(formatter: ResponseFormatter) -> None:
    """Тест экранирования HTML."""
    track = TrackInfo(
        track_id="123",
        title="<script>alert('XSS')</script>",
        artists=["Artist & Band"],
        duration_ms=180000,
        album="Album > Other",
        album_cover_url=None,
        track_url="https://example.com",
    )

    result = formatter.format_track_info(track)

    assert "&lt;script&gt;" in result
    assert "&amp;" in result
    assert "&gt;" in result
    assert "<script>" not in result


def test_format_duration(formatter: ResponseFormatter) -> None:
    """Тест форматирования длительности."""
    # Проверим разные длительности
    test_cases = [
        (60000, "01:00"),   # 1 минута
        (120000, "02:00"),  # 2 минуты
        (180000, "03:00"),  # 3 минуты
        (90000, "01:30"),   # 1:30
        (3661000, "61:01"), # > 60 минут
    ]

    for duration_ms, expected in test_cases:
        track = TrackInfo(
            track_id="123",
            title="Test",
            artists=["Artist"],
            duration_ms=duration_ms,
            album=None,
            album_cover_url=None,
            track_url="https://example.com",
        )
        result = formatter.format_track_info(track)
        assert expected in result, f"Failed for {duration_ms}ms"
