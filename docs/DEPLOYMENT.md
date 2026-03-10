# Инструкция по деплою

## Требования к серверу

- **ОС**: Ubuntu 22.04 LTS / Debian 11+
- **Python**: 3.11+
- **RAM**: от 512MB
- **CPU**: от 1 ядра

## Подготовка сервера

### 1. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка Python

```bash
sudo apt install python3.11 python3.11-venv python3-pip -y
```

### 3. Установка Redis (опционально)

```bash
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 4. Создание пользователя

```bash
sudo useradd -m -s /bin/bash yambot
sudo passwd yambot
```

## Деплой приложения

### 1. Клонирование репозитория

```bash
sudo -u yambot -i
cd ~
git clone <repo-url> app
cd app
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

Добавьте токен бота и другие настройки:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=30
CACHE_TTL_SECONDS=86400
```

## Systemd сервис

### 1. Создание service файла

```bash
sudo nano /etc/systemd/system/yambot.service
```

Содержимое:

```ini
[Unit]
Description=YAM Telegram Bot
After=network.target

[Service]
Type=simple
User=yambot
WorkingDirectory=/home/yambot/app
Environment="PATH=/home/yambot/app/venv/bin"
ExecStart=/home/yambot/app/venv/bin/python /home/yambot/app/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Включение и запуск сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl enable yambot
sudo systemctl start yambot
sudo systemctl status yambot
```

### 3. Полезные команды

```bash
# Проверить статус
sudo systemctl status yambot

# Перезапустить
sudo systemctl restart yambot

# Остановить
sudo systemctl stop yambot

# Посмотреть логи
sudo journalctl -u yambot -f

# Посмотреть логи за сегодня
sudo journalctl -u yambot --since today
```

## Настройка firewall

```bash
# Разрешить SSH
sudo ufw allow 22/tcp

# Включить firewall
sudo ufw enable

# Проверить статус
sudo ufw status
```

## Настройка логов

Логи приложения находятся в `logs/` директории:

- `bot_YYYY-MM-DD.log` — логи за день
- Ротация: каждый день
- Хранение: 30 дней
- Компрессия: zip

## Обновление

### 1. Обновление кода

```bash
cd ~/app
git pull
```

### 2. Обновление зависимостей

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 3. Перезапуск сервиса

```bash
sudo systemctl restart yambot
```

## Мониторинг

### Проверка логов

```bash
# Логи systemd
sudo journalctl -u yambot -f

# Логи приложения
tail -f ~/app/logs/bot_$(date +%Y-%m-%d).log
```

### Метрики (опционально)

Можно интегрировать с:
- Prometheus + Grafana
- Sentry (для ошибок)
- Custom webhook

## Docker (опционально)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: always
    env_file: .env
    depends_on:
      - redis

  redis:
    image: redis:alpine
    restart: always
```

### Запуск

```bash
docker-compose up -d
```

## Безопасность

1. **Не коммитьте** `.env` файл в git
2. Используйте **сложные пароли** для пользователя yambot
3. Ограничьте **доступ** к `.env` файлу:
```bash
chmod 600 .env
```
4. Регулярно **обновляйте** зависимости:
```bash
pip list --outdated
pip install --upgrade package_name
```

## Troubleshooting

### Бот не запускается

```bash
# Проверить логи
sudo journalctl -u yambot -n 50

# Проверить конфигурацию
python -c "from src.config import get_settings; print(get_settings())"
```

### Ошибки импорта

```bash
# Переустановить зависимости
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Проблемы с токеном

- Проверьте, что токен корректный в `.env`
- Проверьте, что токен не истёк в @BotFather
