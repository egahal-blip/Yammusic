import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.app import create_application
from src.utils.logger import log, setup_logger


async def main() -> None:
    """Главная функция"""
    setup_logger()
    log.info("Starting bot...")

    application = create_application()

    # Запуск бота с polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    log.info("Bot started successfully!")

    # Держать бота запущенным
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        log.info("Shutting down bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())

