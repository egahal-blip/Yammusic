import asyncio
import sys
from datetime import datetime, time
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.app import create_application
from src.bot.handlers.track import cache
from src.utils.logger import log, setup_logger
from src.config import get_settings


def seconds_until_midnight() -> float:
    """Рассчитать количество секунд до следующей полуночи."""
    now = datetime.now()
    midnight = datetime.combine(now.date(), time(0, 0))
    if now >= midnight:
        midnight = midnight.replace(day=midnight.day + 1)
    return (midnight - now).total_seconds()


async def daily_cache_cleanup() -> None:
    """Фоновая задача для ежедневной очистки кеша в полночь."""
    while True:
        seconds = seconds_until_midnight()
        log.info(f"Next cache cleanup in {int(seconds // 3600)}h {int((seconds % 3600) // 60)}m")

        await asyncio.sleep(seconds)

        log.info("Running daily cache cleanup...")
        deleted = await cache.cleanup_expired()
        log.info(f"Cache cleanup completed: {deleted} expired entries removed")


async def main() -> None:
    """Главная функция"""
    setup_logger()
    log.info("Starting bot...")

    settings = get_settings()
    application = create_application()

    # Запуск фоновой задачи для очистки кеша
    cleanup_task = asyncio.create_task(daily_cache_cleanup())

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

        # Остановить фоновую задачу очистки кеша
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

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
