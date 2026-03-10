# Руководство для разработки

## Установка окружения для разработки

1. Клонируйте репозиторий
```bash
git clone <repo-url>
cd yam-bot
```

2. Создайте виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости
```bash
pip install -r requirements.txt
```

## Запуск тестов

### Запустить все тесты
```bash
pytest
```

### Запустить с coverage
```bash
pytest --cov=src --cov-report=html
```

### Запустить конкретный тест
```bash
pytest tests/unit/test_config.py
```

## Кодстайл

### Форматирование кода
```bash
black src/
```

### Линтинг
```bash
ruff check src/
```

### Типизация
```bash
mypy src/
```

## Структура проекта

```
src/
├── bot/                    # Telegram-бот
│   ├── app.py             # Инициализация приложения
│   ├── handlers/          # Обработчики команд
│   ├── middlewares/       # Middleware
│   └── keyboards/         # Inline клавиатуры
├── services/              # Бизнес-логика
│   ├── yandex_music.py    # Клиент Яндекс.Музыки
│   ├── url_parser.py      # Парсер ссылок
│   ├── formatter.py       # Форматирование ответов
│   ├── cache.py           # Сервис кеширования
│   └── rate_limiter.py    # Rate limiting
├── models/                # Модели данных
│   ├── track.py           # Модель трека
│   └── request.py         # Модель запроса
├── utils/                 # Утилиты
│   ├── logger.py          # Логирование
│   ├── validators.py      # Валидаторы
│   └── exceptions.py      # Кастомные исключения
├── locale/                # Локализация
│   └── ru/                # Русский язык
├── config.py              # Конфигурация
└── main.py                # Точка входа
```

## Добавление новых команд

1. Создайте файл в `src/bot/handlers/`
```python
# mycommand.py
from telegram import Update
from telegram.ext import ContextTypes

async def mycommand_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /mycommand"""
    await update.message.reply_text("Ответ")
```

2. Зарегистрируйте handler в `src/bot/app.py`
```python
from .handlers import mycommand

application.add_handler(CommandHandler("mycommand", mycommand.mycommand_command))
```

## Добавление новых тестов

Создайте файл в `tests/unit/` или `tests/integration/`:

```python
# tests/unit/test_myfeature.py
import pytest
from src.services import myfeature

def test_myfeature():
    result = myfeature.do_something()
    assert result == "expected"
```

## Конвенции

- **Имена файлов**: `snake_case.py`
- **Имена классов**: `PascalCase`
- **Имена функций**: `snake_case`
- **Константы**: `UPPER_CASE`
- **Документация**: Docstrings для всех публичных функций и классов

## Логирование

Используйте логгер из `src.utils.logger`:

```python
from src.utils.logger import log

log.info("Info message")
log.warning("Warning message")
log.error("Error message")
log.debug("Debug message")
```

## Конфигурация

Доступ к настройкам через `get_settings()`:

```python
from src.config import get_settings

settings = get_settings()
token = settings.telegram_bot_token
```

## Полезные команды

### Создать миграцию (если используется БД)
```bash
alembic revision --autogenerate -m "description"
```

### Применить миграции
```bash
alembic upgrade head
```

### Запустить бота в dev режиме
```bash
python src/main.py
```

### Запустить бота с hot reload (опционально)
```bash
# Установите watchfiles
pip install watchfiles
python src/main.py --reload
```
