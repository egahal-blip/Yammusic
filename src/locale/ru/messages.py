"""Русские текстовые сообщения бота."""

# Команда /start
START_MESSAGE = """👋 Привет, {first_name}!

Я — бот для получения информации о треках из Яндекс.Музыки.

🎵 <b>Как пользоваться:</b>
Просто отправь мне ссылку на трек из Яндекс.Музыки, и я покажу информацию о нём.

📎 <b>Пример ссылки:</b>
https://music.yandex.ru/album/12345/track/67890

❓ Для справки нажми /help"""


# Команда /help
HELP_MESSAGE = """📖 <b>Справка</b>

<b>Доступные команды:</b>
/start — Запустить бота
/help — Показать эту справку
/about — О боте
/stats — Статистика бота

<b>Как пользоваться:</b>
Отправь мне ссылку на трек из Яндекс.Музыки, и я покажу информацию о нём.

<b>Поддерживаемые форматы ссылок:</b>
• https://music.yandex.ru/album/XXX/track/YYY
• https://music.yandex.ru/track/YYY"""


# Команда /about
ABOUT_MESSAGE = """ℹ️ <b>О боте</b>

<b>YAM Info Bot</b> — Telegram бот для получения информации о треках из Яндекс.Музыки.

<b>Возможности:</b>
• Быстрый поиск информации о треке
• Отображение названия, артиста, альбома
• Ссылка на прослушивание

<b>Версия:</b> 1.0.0
<b>Разработчик:</b> @your_username"""


# Команда /stats
STATS_MESSAGE = """📊 <b>Статистика бота</b>

⏱ Uptime: <code>{uptime}</code>
📨 Всего запросов: <code>{total_requests}</code>
✅ Успешных: <code>{successful_requests}</code>
❌ Ошибок: <code>{failed_requests}</code>
📈 Success Rate: <code>{success_rate:.1f}%</code>
⚡ Среднее время: <code>{avg_response_time:.2f}s</code>
👥 Пользователей: <code>{unique_users}</code>"""


# Сообщения об ошибках
ERRORS = {
    "invalid_url": (
        "❌ Неверный формат ссылки.\n\n"
        "Отправьте ссылку на трек Яндекс.Музыки.\n"
        "Пример: https://music.yandex.ru/album/12345/track/67890"
    ),
    "track_not_found": (
        "🔍 Трек не найден.\n\n"
        "Проверьте правильность ссылки."
    ),
    "api_error": (
        "⚠️ Ошибка при получении данных.\n\n"
        "Попробуйте позже."
    ),
    "rate_limit": (
        "⏳ Слишком много запросов.\n\n"
        "Подождите немного и попробуйте снова."
    ),
    "timeout": (
        "⏱ Превышено время ожидания.\n\n"
        "Попробуйте позже."
    ),
    "unknown": (
        "❌ Произошла ошибка.\n\n"
        "Попробуйте снова."
    ),
}


# Форматирование информации о треке
def format_track_info(
    title: str,
    artists: str,
    duration: str,
    album: str | None = None,
    track_url: str = "",
) -> str:
    """Форматировать информацию о треке.

    Args:
        title: Название трека
        artists: Артисты
        duration: Длительность
        album: Альбом (опционально)
        track_url: Ссылка на трек

    Returns:
        Отформатированная строка
    """
    lines = [
        f"🎵 <b>{_escape_html(title)}</b>",
        f"👤 {_escape_html(artists)}",
        f"⏱ {duration}",
    ]

    if album:
        lines.append(f"📀 Альбом: {_escape_html(album)}")

    if track_url:
        lines.append(f"\n🔗 {track_url}")

    return "\n".join(lines)


def _escape_html(text: str) -> str:
    """Экранировать HTML символы."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
