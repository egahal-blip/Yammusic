"""Обработчик команды /help."""

from telegram import Update
from telegram.ext import ContextTypes
from src.locale.ru.messages import HELP_MESSAGE


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help.

    Args:
        update: Объект обновления Telegram
        context: Контекст бота
    """
    await update.message.reply_text(HELP_MESSAGE, parse_mode="HTML")
