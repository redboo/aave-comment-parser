import logging
import time

import requests


def parse_topics(limit: int = 0) -> list[dict]:
    """
    Функция получает список тем из форума Aave Governance, используя API. Можно
    указать максимальное количество тем с помощью параметра `limit`. Возвращает
    список словарей-тем. Каждый словарь содержит информацию о теме, такую как
    заголовок, автор, количество ответов и т.д.
    """
    url = "https://governance.aave.com/latest.json"
    params = {"no_definitions": "true", "page": 0}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
    }
    session = requests.Session()
    topics = []

    while True:
        try:
            response = session.get(url, params=params, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 429:
                raise

            logging.warning("Слишком много запросов, ожидание 5 секунд")
            time.sleep(5)
            continue
        data = response.json()
        if not data["topic_list"]["topics"]:
            break
        topics.extend(data["topic_list"]["topics"])
        params["page"] += 1

        if params["page"] % 10 == 0:
            logging.info(f"Обработано {len(topics)} тем из {params['page']} страниц")

        if limit and limit <= len(topics):
            break

    logging.info(f"Обработано {len(topics)} тем из {params['page']} страниц")
    return topics[:limit] or topics
