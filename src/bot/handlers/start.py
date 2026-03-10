from telegram import Update
from telegram.ext import ContextTypes
from src.utils.logger import log
from src.locale.ru.messages import START_MESSAGE


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start.

    Args:
        update: Объект обновления Telegram
        context: Контекст бота
    """
    user = update.effective_user
    log.info(f"User {user.id} (@{user.username}) started the bot")

    welcome_message = START_MESSAGE.format(first_name=user.first_name)

    await update.message.reply_text(welcome_message, parse_mode="HTML")
