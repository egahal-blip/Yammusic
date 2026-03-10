"""Обработчик сообщений со ссылками на треки."""

import time
from telegram import Update
from telegram.ext import ContextTypes

from src.services.url_parser import YandexMusicURLParser
from src.services.yandex_music import YandexMusicService
from src.services.formatter import ResponseFormatter
from src.services.rate_limiter import InMemoryRateLimiter
from src.services.cache import InMemoryCache
from src.utils.exceptions import (
    InvalidURLError,
    TrackNotFoundError,
    YandexMusicAPIError,
    RateLimitError,
    TimeoutError as YAMTimeoutError,
)
from src.utils.logger import log
from src.utils.metrics import metrics
from src.config import get_settings

settings = get_settings()

# Singleton сервисы
url_parser = YandexMusicURLParser()
cache = InMemoryCache(ttl_seconds=settings.cache_ttl_seconds)
ym_service = YandexMusicService(
    cache=cache,
    timeout_seconds=settings.api_timeout_seconds,
    max_retries=settings.api_max_retries,
)
formatter = ResponseFormatter()
rate_limiter = InMemoryRateLimiter(
    max_requests=settings.rate_limit_per_minute,
    window_seconds=60,
)


async def handle_track_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик сообщений со ссылками на треки.

    Args:
        update: Объект обновления Telegram
        context: Контекст бота
    """
    start_time = time.time()
    user = update.effective_user
    message_text = update.message.text

    log.info(f"[REQUEST] User {user.id} (@{user.username}): {message_text[:50]}...")

    try:
        # Проверить rate limit
        await rate_limiter.check_limit(user.id)
        remaining = await rate_limiter.get_remaining_requests(user.id)
        log.debug(f"[RATE_LIMIT] User {user.id} has {remaining} requests remaining")

        # Распарсить URL
        parsed = url_parser.parse(message_text)
        log.debug(f"[PARSER] Parsed track_id: {parsed.track_id}")

        # Получить информацию о треке
        track = await ym_service.get_track_info(parsed.track_id)
        log.debug(f"[API] Retrieved track: {track.title} - {track.artists_formatted}")

        # Отправить ответ
        response = formatter.format_track_info(track)
        await update.message.reply_text(response, parse_mode="HTML")

        duration = time.time() - start_time
        log.info(f"[SUCCESS] User {user.id} | Track: {track.title} | Duration: {duration:.2f}s")

        # Записать метрики
        metrics.record_request(user.id, success=True, duration=duration)

    except InvalidURLError:
        duration = time.time() - start_time
        log.warning(f"[INVALID_URL] User {user.id} | Duration: {duration:.2f}s")
        await update.message.reply_text(formatter.format_error("invalid_url"))
        metrics.record_request(user.id, success=False, duration=duration, error_type="invalid_url")

    except TrackNotFoundError:
        duration = time.time() - start_time
        log.warning(f"[NOT_FOUND] User {user.id} | Duration: {duration:.2f}s")
        await update.message.reply_text(formatter.format_error("track_not_found"))
        metrics.record_request(user.id, success=False, duration=duration, error_type="track_not_found")

    except YandexMusicAPIError as e:
        duration = time.time() - start_time
        log.error(f"[API_ERROR] User {user.id} | Error: {str(e)} | Duration: {duration:.2f}s")
        await update.message.reply_text(formatter.format_error("api_error"))
        metrics.record_request(user.id, success=False, duration=duration, error_type="api_error")

    except RateLimitError as e:
        duration = time.time() - start_time
        log.warning(f"[RATE_LIMIT] User {user.id} | Duration: {duration:.2f}s")
        await update.message.reply_text(formatter.format_error("rate_limit"))
        metrics.record_request(user.id, success=False, duration=duration, error_type="rate_limit")

    except YAMTimeoutError as e:
        duration = time.time() - start_time
        log.error(f"[TIMEOUT] User {user.id} | Duration: {duration:.2f}s")
        await update.message.reply_text(formatter.format_error("timeout"))
        metrics.record_request(user.id, success=False, duration=duration, error_type="timeout")

    except Exception as e:
        duration = time.time() - start_time
        log.error(f"[ERROR] User {user.id} | Error: {str(e)} | Duration: {duration:.2f}s")
        await update.message.reply_text(formatter.format_error("unknown"))
        metrics.record_request(user.id, success=False, duration=duration, error_type="unknown")
