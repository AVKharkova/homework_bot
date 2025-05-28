# Homework Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-v4.x-blue?logo=telegram)

Telegram-бот на Python, который отслеживает статусы заданий через API Яндекс Практикума и отправляет уведомления в Telegram-чат.

---

## Возможности

- Проверяет статусы заданий на [эндпоинте](https://practicum.yandex.ru/api/user_api/homework_statuses/) Яндекс Практикума (раз в 10 минут)
- Отправляет сообщения в Telegram c результатами проверки
- Логирует все ключевые события и ошибки (stdout и файл логов)
- Обрабатывает все ошибки API и Telegram

---

## Установка и запуск

1. Клонируйте проект:
    ```bash
    git clone https://github.com/AVKharkova/homework_bot.git
    cd homework_bot
    ```

2. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4. Создайте файл `.env` в корне проекта и добавьте переменные:
    ```
    PRACTICUM_TOKEN=токен_практикума
    TELEGRAM_TOKEN=токен_бота_telegram
    TELEGRAM_CHAT_ID=ваш_id_чата
    ```

5. Запустите бота:
    ```bash
    python homework.py
    ```

---

## Логирование

- Фиксация времени, уровня события (DEBUG, ERROR, CRITICAL) и описания
- Ключевые логи:
  - Отсутствие переменных окружения (CRITICAL)
  - Успешная отправка сообщений (DEBUG)
  - Ошибки Telegram или API (ERROR)
  - Неожиданные форматы ответа (ERROR)
  - Отсутствие новых статусов (DEBUG)

Все логи доступны в stdout и в файле `main.log`.

---

## Технологии

- Python 3.9+
- pyTelegramBotAPI
- requests
- python-dotenv

---

## Автор
**[Анастасия Харькова](https://github.com/AVKharkova)**
