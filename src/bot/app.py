from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.config import get_settings
from src.utils.logger import log
from .handlers import start, help, about, track, stats

settings = get_settings()


def create_application() -> Application:
    """Создание и настройка приложения бота"""

    application = Application.builder().token(settings.telegram_bot_token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", help.help_command))
    application.add_handler(CommandHandler("about", about.about_command))
    application.add_handler(CommandHandler("stats", stats.stats_command))

    # Message handlers (последним!)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, track.handle_track_link)
    )

    log.info("Application created successfully")
    return application

