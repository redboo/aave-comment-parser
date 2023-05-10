import logging

import requests

from comments_parser import parse_comments
from topics_parser import parse_topics
from utils import plural


def parse_topics_and_comments(csv_file: str, limit: int | None = None) -> int:
    num_comments = 0

    try:
        topics = parse_topics(limit=limit)
        count_topics = len(topics)

        for i, topic in enumerate(topics, start=1):
            logging.info(f"Парсинг комментариев ({i}/{count_topics}) - {topic['title']}")
            try:
                num = parse_comments(topic, csv_file)
                num_comments += num
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException,
            ):
                logging.error("Ошибка подключения")
                break
            except Exception:
                logging.exception("Ошибка при обработке комментариев")
                break
            logging.info(
                f"Собрано {plural(num, ['комментарий', 'комментария', 'комментариев'])} для темы: {topic['title']}"
            )
    except Exception:
        logging.error("Не удалось получить список тем-топиков")

    return num_comments
