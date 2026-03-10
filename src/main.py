import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.app import create_application
from src.utils.logger import log, setup_logger
from src.config import get_settings


async def main() -> None:
    """Главная функция"""
    setup_logger()
    log.info("Starting bot...")

    settings = get_settings()
    application = create_application()

    await application.initialize()

    if settings.use_webhook:
        # Webhook mode
        log.info(f"Starting webhook mode on {settings.webhook_host}:{settings.webhook_port}")
        log.info(f"Webhook URL: {settings.webhook_url}")

        await application.bot.set_webhook(
            url=settings.webhook_url,
            secret_token=settings.webhook_secret_token if settings.webhook_secret_token else None,
        )
        log.info("Webhook set successfully")

        await application.start()

        # Запуск webhook сервера
        await application.updater.start_webhook(
            listen=settings.webhook_host,
            port=settings.webhook_port,
            url_path=settings.webhook_path.lstrip("/"),
            drop_pending_updates=True,
        )

        log.info(f"Bot started successfully via webhook on port {settings.webhook_port}!")

    else:
        # Polling mode (development)
        log.info("Starting polling mode (development)")
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        log.info("Bot started successfully via polling!")

    # Держать бота запущенным
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        log.info("Shutting down bot...")

        if settings.use_webhook:
            await application.updater.stop_webhook()
            await application.bot.delete_webhook()
        else:
            await application.updater.stop()

        await application.stop()
        await application.shutdown()
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
