import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from telebot import TeleBot
from dotenv import load_dotenv

# Пишем логи в файл
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s',
    filename='main.log',
    encoding='utf-8',
)

logger = logging.getLogger(__name__)

# Дополнительно выводим логи в консоль
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s - %(name)s'
))
logger.addHandler(stream_handler)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Метка времени для отладки = 1731628800
TEST_TIMESTAMP = int(time.time())


def check_tokens():
    """Проверка переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправка сообщение в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Вам телеграмма: "{message}"')
    except Exception as error:
        logger.error(f'Сбой при отправке телеграммы: {error}')


def get_api_answer(timestamp):
    """Запрос к API Практикума."""
    logger.debug('Запрос к API Практикума.')
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                f'Эндпоинт {ENDPOINT} недоступен: {response.status_code}'
            )
        return response.json()
    except Exception as error:
        raise ConnectionError(f'Ошибка при запросе к API: {error}')


def check_response(response):
    """Проверяет корректность ответа API."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарём.')

    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Отсутствуют ключи homeworks или current_date.')

    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError('Значение по ключу homeworks не является списком.')

    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе отсутствует ключ homework_name')
    if 'status' not in homework:
        raise KeyError('В ответе отсутствует ключ status')

    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы: {homework_status}')

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения.')
        sys.exit('Работа бота остановлена.')

    # Создаем объект класса бота
    bot = TeleBot(TELEGRAM_TOKEN)

    timestamp = TEST_TIMESTAMP
    last_error_message = None

    logger.info('Бот запущен и готов к работе.')

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            timestamp = response.get('current_date', timestamp)

            if homeworks:
                homework = homeworks[0]
                message_text = parse_status(homework)
                send_message(bot, message_text)
            else:
                logger.debug('Новых статусов нет.')

        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            logger.error(error_message)
            if error_message != last_error_message:
                send_message(bot, error_message)
                last_error_message = error_message

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
