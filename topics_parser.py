import logging
import time

import requests


def parse_topics(limit=None):
    """
    Функция получает список тем из форума Aave Governance, используя API. Можно
    указать максимальное количество тем с помощью параметра `limit`. Возвращает
    список объектов-тем. Каждый объект содержит информацию о теме, такую как
    заголовок, автор, количество ответов и т.д.
    """
    url = "https://governance.aave.com/latest.json"
    params = {"no_definitions": "true", "page": 0}
    session = requests.Session()
    topics = []

    while True:
        try:
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.warning("Слишком много запросов, ожидание 5 секунд")
                time.sleep(5)
                continue
            else:
                raise e

        data = response.json()
        topics.extend(data["topic_list"]["topics"])
        params["page"] += 1

        if not data["topic_list"]["topics"]:
            if limit and len(topics) < limit:
                logging.error("Не удалось получить темы")
                raise ValueError("Не удалось получить темы")
            else:
                break

        if limit and len(topics) >= limit:
            break

        if params["page"] % 10 == 0:
            logging.info(f"Обработано {len(topics)} тем из {params['page']} страниц")

    return topics[:limit] if limit else topics
