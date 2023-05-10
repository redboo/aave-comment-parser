"""Модуль для парсинга комментариев с сайта."""

import logging
import time
from datetime import datetime

import click

from parsing import parse_topics_and_comments
from utils import convert_csv_to_excel, create_csv_file, plural


def setup_logging(level: str) -> None:
    """Настройка логирования.

    Args:
        level (str): Уровень логирования.
    """
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s: %(message)s")


@click.command()
@click.option(
    "--interval",
    default=None,
    type=int,
    help="Установите интервал в секундах для автоматического парсинга (по умолчанию не установлен)",
)
@click.option(
    "--log",
    default="WARNING",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Установите уровень логирования (по умолчанию: WARNING)",
)
@click.option(
    "--csv",
    is_flag=True,
    default=False,
    help="Укажите этот параметр, чтобы сохранить данные в CSV-файл (по умолчанию: сохранять)",
)
@click.option(
    "--excel",
    is_flag=True,
    default=False,
    help="Укажите этот параметр, чтобы сохранить данные в Excel-файл (по умолчанию: не сохранять)",
)
@click.option(
    "--limit",
    default=None,
    type=int,
    help="Укажите максимальное количество тем-топиков для парсинга (по умолчанию не ограничено)",
)
def run(
    log: str,
    interval: int | None = None,
    csv: bool = False,
    excel: bool = False,
    limit: int | None = None,
) -> None:
    """Запускает скрипт для парсинга комментариев с сайта.

    Args:
        log_level (str): Уровень логирования.
        interval (int, optional): Интервал в секундах для автоматического парсинга. Defaults to None.
        csv (bool, optional): Сохранять данные в CSV-файл. Defaults to False.
        excel (bool, optional): Сохранять данные в Excel-файл. Defaults to False.
        limit (int, optional): Максимальное количество тем-топиков для парсинга. Defaults to None.
    """
    setup_logging(log)
    excel_file = None

    while True:
        csv_file = create_csv_file(
            filename_suffix="aave-comments",
            headers=["Topic", "Likes", "Views", "Comment", "User", "Comment likes", "Date"],
        )
        start_time = time.monotonic()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Парсинг запущен...")
        num_comments = parse_topics_and_comments(csv_file, limit=limit)

        if excel or csv:
            excel_file = csv_file[:-3] + "xlsx"
            csv_file, excel_file = convert_csv_to_excel(csv_file, output_csv=csv, output_excel=excel)

        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Парсинг завершен. "
            f"{plural(num_comments, ['комментарий', 'комментария', 'комментариев'])} "
            f"cохранено в: {excel_file or csv_file}"
        )

        if interval:
            elapsed_time = time.monotonic() - start_time
            elapsed_time = elapsed_time if elapsed_time >= 0 else 0
            if (sleep_length := interval - elapsed_time) > 0:
                time.sleep(sleep_length)
        else:
            break


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
