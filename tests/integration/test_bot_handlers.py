"""Интеграционные тесты для handlers бота."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from src.bot.handlers import track, start, help, about
from src.services.url_parser import YandexMusicURLParser
from src.services.yandex_music import YandexMusicService


@pytest.fixture
def mock_update():
    """Создать mock Update."""
    user = User(id=123, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=123, type="private")
    message = MagicMock(spec=Message)
    message.message_id = 1
    message.chat = chat
    message.from_user = user
    message.text = "https://music.yandex.ru/track/12345"
    message.reply_text = AsyncMock()

    update = MagicMock(spec=Update)
    update.update_id = 1
    update.message = message
    update.effective_user = user

    return update


@pytest.mark.asyncio
async def test_start_command(mock_update) -> None:
    """Тест команды /start."""
    mock_update.message.text = "/start"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await start.start_command(mock_update, context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args
    text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
    assert "Привет" in text or "Hello" in text or "Yandex" in text


@pytest.mark.asyncio
async def test_help_command(mock_update) -> None:
    """Тест команды /help."""
    mock_update.message.text = "/help"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await help.help_command(mock_update, context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args
    text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
    assert "Справка" in text or "music.yandex.ru" in text


@pytest.mark.asyncio
async def test_about_command(mock_update) -> None:
    """Тест команды /about."""
    mock_update.message.text = "/about"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await about.about_command(mock_update, context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args
    text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
    assert "бот" in text.lower() or "YAM" in text


@pytest.mark.asyncio
async def test_handle_track_link_invalid_url(mock_update) -> None:
    """Тест обработки невалидного URL."""
    mock_update.message.text = "https://google.com"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await track.handle_track_link(mock_update, context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args
    text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
    assert "Неверный" in text or "невалидный" in text.lower() or "format" in text.lower()


def test_url_parser_integration() -> None:
    """Тест интеграции URL парсера."""
    parser = YandexMusicURLParser()

    # Валидные URL
    valid_urls = [
        "https://music.yandex.ru/album/123/track/456",
        "https://music.yandex.ru/track/789",
    ]

    for url in valid_urls:
        result = parser.parse(url)
        assert result.track_id is not None
        assert result.original_url == url

    # Невалидные URL
    from src.utils.exceptions import InvalidURLError

    invalid_urls = [
        "https://google.com",
        "not a url",
        "",
    ]

    for url in invalid_urls:
        with pytest.raises(InvalidURLError):
            parser.parse(url)


@pytest.mark.asyncio
async def test_yandex_music_service_initialization() -> None:
    """Тест инициализации сервиса Яндекс.Музыки."""
    service = YandexMusicService(token=None)

    assert service is not None
    assert service._initialized is False

    await service.close()


@pytest.mark.asyncio
async def test_track_handler_with_mock_service(mock_update) -> None:
    """Тест обработчика с замоканным сервисом."""
    mock_update.message.text = "https://music.yandex.ru/track/12345"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Mock сервис
    with patch.object(track, "ym_service") as mock_ym:
        from src.models import TrackInfo

        mock_track = TrackInfo(
            track_id="12345",
            title="Test Track",
            artists=["Test Artist"],
            duration_ms=180000,
            album="Test Album",
            album_cover_url="https://example.com/cover.jpg",
            track_url="https://music.yandex.ru/track/12345",
        )

        mock_ym.get_track_info = AsyncMock(return_value=mock_track)

        await track.handle_track_link(mock_update, context)

        mock_ym.get_track_info.assert_called_once_with("12345")
        mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_track_handler_track_not_found(mock_update) -> None:
    """Тест обработчика когда трек не найден."""
    mock_update.message.text = "https://music.yandex.ru/track/99999"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    # Mock сервис
    with patch.object(track, "ym_service") as mock_ym:
        from src.utils.exceptions import TrackNotFoundError

        mock_ym.get_track_info = AsyncMock(side_effect=TrackNotFoundError("Not found"))

        await track.handle_track_link(mock_update, context)

        mock_update.message.reply_text.assert_called_once()
