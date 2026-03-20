from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest
from src.config import get_settings
from src.utils.logger import log
from .handlers import start, help, about, track, stats

settings = get_settings()


def create_application() -> Application:
    """Создание и настройка приложения бота"""

    # Настраиваем HTTP-клиент с увеличенными таймаутами для надежности
    httpx_request = HTTPXRequest(
        connect_timeout=20.0,  # Таймаут подключения
        read_timeout=20.0,     # Таймаут чтения
        write_timeout=20.0,    # Таймаут записи
        pool_timeout=10.0,     # Таймаут получения соединения из пула
    )

    builder = Application.builder().token(settings.telegram_bot_token).request(httpx_request)

    # Добавляем прокси если настроен (некоторые хостинги блокируют Telegram API)
    if settings.telegram_proxy_url:
        log.info(f"Using proxy: {settings.telegram_proxy_url}")
        builder = builder.proxy_url(settings.telegram_proxy_url)

    application = builder.build()

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

