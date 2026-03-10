"""Обработчик команды /about."""

from telegram import Update
from telegram.ext import ContextTypes
from src.locale.ru.messages import ABOUT_MESSAGE


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /about.

    Args:
        update: Объект обновления Telegram
        context: Контекст бота
    """
    await update.message.reply_text(ABOUT_MESSAGE, parse_mode="HTML")
