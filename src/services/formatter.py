"""Форматирование ответов для пользователя."""

from src.models import TrackInfo
from src.locale.ru import messages as msg


class ResponseFormatter:
    """Форматирование ответов для пользователя."""

    def format_track_info(self, track: TrackInfo) -> str:
        """Форматировать информацию о треке.

        Args:
            track: Информация о треке

        Returns:
            Отформатированная строка для отправки пользователю
        """
        return msg.format_track_info(
            title=track.title,
            artists=track.artists_formatted,
            duration=track.duration_formatted,
            album=track.album,
            track_url=track.track_url,
        )

    def format_error(self, error_type: str, details: str = "") -> str:
        """Форматировать сообщение об ошибке.

        Args:
            error_type: Тип ошибки
            details: Дополнительные детали

        Returns:
            Отформатированное сообщение об ошибке
        """
        message = msg.ERRORS.get(error_type, msg.ERRORS["unknown"])

        if details:
            message += f"\n\n<i>{self._escape_html(details)}</i>"

        return message

    @staticmethod
    def _escape_html(text: str) -> str:
        """Экранировать HTML символы.

        Args:
            text: Текст для экранирования

        Returns:
            Экранированный текст
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
