from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserRequest(BaseModel):
    """Модель запроса пользователя"""

    user_id: int = Field(..., description="ID пользователя Telegram")
    username: Optional[str] = Field(None, description="Username")
    track_url: str = Field(..., description="URL трека")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(..., description="Успешность запроса")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
