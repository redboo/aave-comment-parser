import argparse
import csv
import logging
import os
import time
from datetime import datetime

import requests

from comments_parser import parse_comments
from topics_parser import parse_topics


def plural(n, forms):
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {forms[0]}"
    elif n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
        return f"{n} {forms[1]}"
    else:
        return f"{n} {forms[2]}"


def setup_logging(level):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s: %(message)s")


def create_csv_file():
    path = "downloads"
    os.makedirs(path, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_file = f"{path}/aave-comments_{now}.csv"

    headers = ["Тема", "Лайки", "Просмотры", "Комментарий", "Пользователь", "Лайки комментария", "Дата"]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    return csv_file


def parse_topics_and_comments(csv_file):
    num_comments = 0

    try:
        topics = parse_topics()
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
            ) as e:
                logging.error("Ошибка подключения")
                break
            logging.info(
                f"Собрано {plural(num, ['комментарий', 'комментария', 'комментариев'])} для темы: {topic['title']}"
            )
    except Exception:
        logging.error("Не удалось получить список тем-топиков")

    return num_comments


def run(log_level, interval=None):
    setup_logging(log_level)
    csv_file = create_csv_file()

    while True:
        start_time = time.monotonic()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Парсинг запущен...")
        num_comments = parse_topics_and_comments(csv_file)
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Парсинг завершен. Сохранено {plural(num_comments, ['комментарий', 'комментария', 'комментариев'])} в файле {csv_file}"
        )

        if interval:
            elapsed_time = time.monotonic() - start_time
            elapsed_time = elapsed_time if elapsed_time >= 0 else 0
            if (sleep_length := args.interval - elapsed_time) > 0:
                time.sleep(sleep_length)
        else:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interval",
        type=int,
        help="Установите интервал в секундах для автоматического парсинга",
    )
    parser.add_argument(
        "--level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    args = parser.parse_args()

    try:
        run(log_level=args.level, interval=args.interval)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
