# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Run tests
pytest                                    # All tests
pytest tests/unit/test_cache.py          # Specific file
pytest --cov=src --cov-report=html       # With coverage

# Code quality
black src/                               # Format code
ruff check src/                          # Lint
mypy src/                                # Type checking

# Run bot (development)
python src/main.py                       # Direct run (Windows: venv\Scripts\python.exe)
```

## Architecture Overview

YAM Bot is a Telegram bot that fetches track information from Yandex Music using a clean layered architecture.

### Request Flow

```
Telegram Message
    ↓
MessageHandler (filters.TEXT & ~filters.COMMAND)
    ↓
track.py::handle_track_link()
    ↓
[Rate Limiter] → [URL Parser] → [Music Service] → [Cache/API] → [Formatter] → [Reply]
```

### Key Architectural Patterns

**Singleton Services in Handlers:** Services are instantiated as module-level singletons in `src/bot/handlers/track.py`. This is intentional for the current architecture — when modifying, be aware that:
- Testing requires mocking at the module level
- Dependencies are injected via constructors (e.g., `YandexMusicService(cache=cache)`)
- All services are async-first

**Pydantic for Everything:** All data models use Pydantic v2 with strict validation. The `TrackInfo` model includes:
- Field validators (e.g., `duration_ms` must be positive)
- Computed properties (e.g., `duration_formatted`, `artists_formatted`)
- JSON serialization via `.model_dump_json()`

**Centralized Error Handling:** Custom exceptions in `src/utils/exceptions.py` are caught in handlers with user-friendly responses via `ResponseFormatter.format_error()`.

**In-Memory State:** Currently uses `InMemoryCache` and `InMemoryRateLimiter` — data is lost on restart. Redis is configured but not implemented (see `.env` for `REDIS_HOST`).

### Critical Files

| File | Purpose |
|------|---------|
| `src/bot/app.py` | Application creation, handler registration |
| `src/bot/handlers/track.py` | Main handler with singleton services |
| `src/services/yandex_music.py` | Yandex Music API client with retry logic |
| `src/config.py` | Pydantic Settings with `@lru_cache` singleton |
| `src/main.py` | Entry point with graceful shutdown |

### Adding New Commands

1. Create handler in `src/bot/handlers/mycommand.py`:
```python
from telegram import Update
from telegram.ext import ContextTypes

async def mycommand_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response")
```

2. Register in `src/bot/app.py`:
```python
from .handlers import mycommand
application.add_handler(CommandHandler("mycommand", mycommand.mycommand_command))
```

### Configuration

Access settings via `get_settings()` — it's cached with `@lru_cache` so calling it multiple times is cheap:
```python
from src.config import get_settings
settings = get_settings()
```

### Logging

Use the pre-configured logger from `src.utils.logger`:
```python
from src.utils.logger import log
log.info("Message")  # Structured with timestamp and level
```

## Deployment Notes

**Minimum Requirements:** 256 MB RAM is sufficient for current architecture (~100-150 MB usage).

**Running Modes:**
- `USE_WEBHOOK=false` — Polling mode (development, single instance)
- `USE_WEBHOOK=true` — Webhook mode (production, supports horizontal scaling)

**Webhook Setup:** Set these in `.env` for production:
```env
USE_WEBHOOK=true
WEBHOOK_URL=https://your-domain.com/telegram-webhook
WEBHOOK_PORT=8443
```

**Systemd:** Use the service file template in `docs/DEPLOYMENT.md` for production deployment.
