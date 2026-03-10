# YAM Bot — Telegram бот для Яндекс.Музыки

## Описание

Telegram-бот для получения информации о треках из Яндекс.Музыки по ссылке.

## Возможности

- 🎵 Получение информации о треке по ссылке
- ⚡ Быстрый ответ (< 2 секунды)
- 🎨 Красивое форматирование
- 🔒 Безопасность (rate limiting)
- 💾 Кеширование запросов

## Установка

### Требования

- Python 3.11+
- pip

### Шаги установки

1. Клонируйте репозиторий
```bash
git clone <repo-url>
cd yam-bot
```

2. Создайте виртуальное окружение
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Установите зависимости
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения
```bash
cp .env.example .env
nano .env  # или любой другой редактор
```

Добавьте токен бота:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

5. Запустите бота
```bash
python src/main.py
```

## Использование

Отправьте боту ссылку на трек Яндекс.Музыки.

### Поддерживаемые форматы ссылок

- `https://music.yandex.ru/album/{id}/track/{id}`
- `https://music.yandex.ru/track/{id}`

## Команды

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/help` | Получить справку |
| `/about` | О боте |

## Технологический стек

- **python-telegram-bot** — библиотека для работы с Telegram API
- **yandex-music** — клиент для Яндекс.Музыки
- **Pydantic** — валидация данных
- **Loguru** — логирование

## Структура проекта

```
yam-bot/
├── src/
│   ├── bot/              # Telegram-бот
│   ├── services/         # Бизнес-логика
│   ├── models/           # Модели данных
│   ├── utils/            # Утилиты
│   └── locale/           # Локализация
├── tests/                # Тесты
├── docs/                 # Документация
└── scripts/              # Скрипты
```

## Разработка

Подробнее см. [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## Деплой

Подробнее см. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Лицензия

MIT
