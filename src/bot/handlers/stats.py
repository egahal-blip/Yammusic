"""Обработчик команды /stats для просмотра метрик."""

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.metrics import metrics
from src.utils.logger import log
from src.locale.ru.messages import STATS_MESSAGE


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats.

    Args:
        update: Объект обновления Telegram
        context: Контекст бота
    """
    user = update.effective_user

    log.info(f"User {user.id} requested stats")

    # Получить сводку метрик
    summary = metrics.get_summary()

    # Форматировать сообщение
    message = STATS_MESSAGE.format(**summary)

    # Добавить типы ошибок если есть
    if summary['error_types']:
        message += "\n\n📋 <b>Ошибки:</b>"
        for error_type, count in summary['error_types'].items():
            message += f"\n• <code>{error_type}</code>: {count}"

    await update.message.reply_text(message, parse_mode="HTML")
