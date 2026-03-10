from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TrackInfo(BaseModel):
    """Модель информации о треке"""

    track_id: str = Field(..., description="ID трека")
    title: str = Field(..., description="Название трека")
    artists: list[str] = Field(..., description="Список артистов")
    duration_ms: int = Field(..., description="Длительность в миллисекундах")
    album: Optional[str] = Field(None, description="Название альбома")
    album_cover_url: Optional[str] = Field(None, description="URL обложки")
    track_url: str = Field(..., description="URL трека")

    @field_validator("duration_ms")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Валидация длительности"""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    @property
    def duration_formatted(self) -> str:
        """Форматированная длительность (ММ:СС)"""
        seconds = self.duration_ms // 1000
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def artists_formatted(self) -> str:
        """Форматированный список артистов"""
        return ", ".join(self.artists)
