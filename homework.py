import logging
import os
import sys
import time
from contextlib import suppress
from http import HTTPStatus

import requests
import telebot
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (
    HTTPStatusError,
    MissingTokenError
)

# Настраиваем логи
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(name)s')
)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler('main.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(name)s')
)
logger.addHandler(file_handler)

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
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Проверка наличия всех переменных окружения."""
    tokens_to_check = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    missing_tokens = [name for name in tokens_to_check if not globals()[name]]
    if missing_tokens:
        missing_tokens_str = (
            'Бот остановлен. Отсутствуют токены: '
            f"{', '.join(missing_tokens)}"
        )
        logger.critical(missing_tokens_str)
        raise MissingTokenError(missing_tokens_str)


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    logger.debug(f'Отправляю сообщение в чат: "{message}"')
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.debug('Сообщение успешно отправлено.')


def get_api_answer(timestamp):
    """Запрос к API Практикума."""
    logger.debug(
        f'Отправляем запрос к {ENDPOINT}, '
        f'params={{"from_date": {timestamp}}}'
    )
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        raise ConnectionError(f'Ошибка при запросе к API: {error}') from error

    if response.status_code != HTTPStatus.OK:
        raise HTTPStatusError(
            f'Сервер вернул статус {response.status_code}'
        )

    return response.json()


def check_response(response):
    """Проверяет корректность ответа API."""
    logger.debug('Начинаю проверку ответа API на корректность.')
    if not isinstance(response, dict):
        raise TypeError(
            f'Ответ API не является словарём. Получен тип: {type(response)}'
        )
    if 'homeworks' not in response:
        raise KeyError('Отсутствует ключ "homeworks" в ответе API.')

    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(
            'Значение по ключу "homeworks" не является списком. '
            f'Получен тип: {type(homeworks)}'
        )

    logger.debug('Проверка ответа API успешно завершена.')
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    logger.debug('Начинаю извлечение статуса домашней работы.')
    missing_keys = [key for key in ('homework_name', 'status')
                    if key not in homework]
    if missing_keys:
        missing_keys_str = ', '.join(missing_keys)
        raise KeyError(f'В ответе отсутствуют ключи: {missing_keys_str}')

    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы: {homework_status}')

    verdict = HOMEWORK_VERDICTS[homework_status]
    result = f'Изменился статус проверки работы "{homework_name}". {verdict}'
    logger.debug(f'Статус успешно извлечён: "{result}"')
    return result


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(TELEGRAM_TOKEN)

    timestamp = int(time.time())
    last_message = ''

    logger.info('Бот запущен и готов к работе.')

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)

            if not homeworks:
                logger.debug('Новых статусов нет.')
                continue

            homework = homeworks[0]
            message_text = parse_status(homework)
            if message_text != last_message:
                send_message(bot, message_text)
                last_message = message_text

            timestamp = response.get('current_date', timestamp)

        except (
            telebot.apihelper.ApiException,
            requests.RequestException
        ) as tg_error:
            logger.exception(
                f'Ошибка при отправке сообщения в Telegram: {tg_error}'
            )

        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            logger.exception(error_message)
            if error_message != last_message:
                with suppress(telebot.apihelper.ApiException):
                    send_message(bot, error_message)
                    last_message = error_message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
