import csv
import datetime
import logging
import time

import requests
from bs4 import BeautifulSoup


def process_comment(comment):
    """Обрабатывает комментарий и возвращает данные об авторе, дате, лайках и тексте комментария."""
    try:
        author = comment.find("span", itemprop="name").text.strip()
        date = comment.find("time").get("datetime")
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        likes = comment.find("meta", itemprop="userInteractionCount")["content"]
        text = comment.find("div", {"class": "post"}).text.strip().replace("\n", " ")
        return author, date, likes, text
    except AttributeError as e:
        raise ValueError(f"Произошла ошибка при обработке комментария: {e}")


def parse_comments(topic, csv_file):
    """Собирает комментарии со страницы и сохраняет их в CSV-файл."""
    num_comments = 0
    url = f"https://governance.aave.com/t/{topic['slug']}"
    logging.info(f"Собираю комментарии со страницы {url}")
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
    )

    while True:
        try:
            res = session.get(url, timeout=10)
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logging.info(f"Страница {url} недоступна.")
                return num_comments
            if e.response.status_code == 429:
                logging.warning("Слишком много запросов. Подождите 5 секунд.")
                time.sleep(5)
                continue
            else:
                logging.error("Ошибка при запросе: %s", e, exc_info=True)
                raise e
        soup = BeautifulSoup(res.text, "html.parser")
        comments = soup.find_all("div", {"class": "crawler-post"})
        next_page_link = None

        for comment in comments:
            if next_page_link := comment.find("a", rel="next"):
                next_page_link = next_page_link.get("href").split("?")[1]
                break
            if comment.find("a", rel="prev"):
                return num_comments

            author, date, likes, text = process_comment(comment)
            num_comments += 1
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([topic["title"], topic["like_count"], topic["views"], text, author, likes, date])

        if next_page_link:
            url = f"{url.split('?')[0]}?{next_page_link}"
        else:
            return num_comments
