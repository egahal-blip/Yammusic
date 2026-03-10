"""Тесты для валидаторов."""

import pytest

from src.utils.validators import (
    validate_track_id,
    validate_album_id,
    sanitize_track_id,
    sanitize_user_input,
    validate_url_format,
    extract_numeric_id,
)


class TestValidateTrackId:
    """Тесты валидации ID трека."""

    def test_valid_track_id(self):
        """Тест валидного ID трека."""
        assert validate_track_id("12345") is True
        assert validate_track_id("1") is True
        assert validate_track_id("9999999999999999999") is True

    def test_invalid_track_id(self):
        """Тест невалидного ID трека."""
        assert validate_track_id("") is False
        assert validate_track_id("abc") is False
        assert validate_track_id("123abc") is False
        assert validate_track_id("12 345") is False


class TestValidateAlbumId:
    """Тесты валидации ID альбома."""

    def test_valid_album_id(self):
        """Тест валидного ID альбома."""
        assert validate_album_id("12345") is True
        assert validate_album_id("1") is True

    def test_invalid_album_id(self):
        """Тест невалидного ID альбома."""
        assert validate_album_id("") is False
        assert validate_album_id("abc") is False
        assert validate_album_id("123abc") is False


class TestSanitizeTrackId:
    """Тесты очистки ID трека."""

    def test_sanitize_clean_id(self):
        """Тест очистки чистого ID."""
        assert sanitize_track_id("12345") == "12345"

    def test_sanitize_dirty_id(self):
        """Тест очистки грязного ID."""
        assert sanitize_track_id("12abc345") == "12345"
        assert sanitize_track_id("track:12345") == "12345"
        assert sanitize_track_id("12-345") == "12345"

    def test_sanitize_empty(self):
        """Тест очистки пустой строки."""
        assert sanitize_track_id("") is None
        assert sanitize_track_id("abc") is None


class TestSanitizeUserInput:
    """Тесты очистки пользовательского ввода."""

    def test_sanitize_normal_text(self):
        """Тест очистки нормального текста."""
        assert sanitize_user_input("Hello world") == "Hello world"
        assert sanitize_user_input("  Hello  ") == "Hello"

    def test_sanitize_max_length(self):
        """Тест обрезки по максимальной длине."""
        long_text = "a" * 2000
        result = sanitize_user_input(long_text, max_length=100)
        assert len(result) == 100

    def test_sanitize_control_chars(self):
        """Тест удаления управляющих символов."""
        text = "Hello\x00world"
        result = sanitize_user_input(text)
        assert result == "Helloworld"


class TestValidateUrlFormat:
    """Тесты валидации формата URL."""

    def test_valid_urls(self):
        """Тест валидных URL."""
        assert validate_url_format("https://example.com") is True
        assert validate_url_format("http://example.com") is True
        assert validate_url_format("https://music.yandex.ru") is True
        assert validate_url_format("https://example.com/path") is True

    def test_invalid_urls(self):
        """Тест невалидных URL."""
        assert validate_url_format("") is False
        assert validate_url_format("not a url") is False
        assert validate_url_format("example.com") is False


class TestExtractNumericId:
    """Тесты извлечения числового ID."""

    def test_extract_from_text(self):
        """Тест извлечения из текста."""
        assert extract_numeric_id("track 12345") == "12345"
        assert extract_numeric_id("id:999") == "999"
        assert extract_numeric_id("123abc456") == "123"

    def test_extract_empty(self):
        """Текст без чисел."""
        assert extract_numeric_id("no numbers") is None
        assert extract_numeric_id("") is None

    def test_extract_first_number(self):
        """Тест извлечения первого числа."""
        assert extract_numeric_id("123 and 456") == "123"
