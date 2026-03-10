"""Тесты для URL парсера."""

import pytest

from src.services.url_parser import YandexMusicURLParser, ParsedURL
from src.utils.exceptions import InvalidURLError

parser = YandexMusicURLParser()


@pytest.mark.parametrize("url,expected_track_id,expected_album_id", [
    ("https://music.yandex.ru/album/12345/track/67890", "67890", "12345"),
    ("https://music.yandex.ru/track/99999", "99999", None),
    ("  https://music.yandex.ru/track/11111  ", "11111", None),
    ("http://music.yandex.ru/album/22222/track/33333", "33333", "22222"),
])
def test_parse_valid_urls(url: str, expected_track_id: str, expected_album_id: str | None) -> None:
    """Тест парсинга валидных URL."""
    result = parser.parse(url)
    assert result.track_id == expected_track_id
    assert result.album_id == expected_album_id


@pytest.mark.parametrize("invalid_url", [
    "https://google.com",
    "not a url",
    "https://music.yandex.ru/album/123",
    "https://music.yandex.ru/artist/123",
    "",
    "  ",
])
def test_parse_invalid_urls(invalid_url: str) -> None:
    """Тест парсинга невалидных URL."""
    with pytest.raises(InvalidURLError):
        parser.parse(invalid_url)


def test_is_valid_url_with_valid() -> None:
    """Тест is_valid_url с валидным URL."""
    assert parser.is_valid_url("https://music.yandex.ru/track/12345") is True


def test_is_valid_url_with_invalid() -> None:
    """Тест is_valid_url с невалидным URL."""
    assert parser.is_valid_url("https://google.com") is False


def test_parsed_url_dataclass() -> None:
    """Тест ParsedURL dataclass."""
    result = parser.parse("https://music.yandex.ru/album/123/track/456")
    assert isinstance(result, ParsedURL)
    assert result.original_url == "https://music.yandex.ru/album/123/track/456"
