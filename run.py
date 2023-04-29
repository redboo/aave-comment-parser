import logging
import time
from datetime import datetime

import click

from parsing import parse_topics_and_comments
from utils import convert_csv_to_excel, create_csv_file, plural


def setup_logging(level):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s: %(message)s")


@click.command()
@click.option(
    "--interval",
    default=None,
    type=int,
    help="Установите интервал в секундах для автоматического парсинга (по умолчанию не установлен)",
)
@click.option(
    "--log-level",
    "--logging",
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
    "--encoding",
    default="utf-8",
    help="Укажите кодировку для сохранения в CSV и Excel (по умолчанию: utf-8)",
)
@click.option(
    "--limit",
    default=None,
    type=int,
    help="Укажите максимальное количество тем-топиков для парсинга (по умолчанию не ограничено)",
)
def run(log_level, interval=None, csv=False, excel=False, limit=None, encoding="utf-8"):
    """
    Скрипт для парсинга комментариев с сайта.
    """
    setup_logging(log_level)
    excel_file = None

    while True:
        csv_file = create_csv_file()
        start_time = time.monotonic()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Парсинг запущен...")
        num_comments = parse_topics_and_comments(csv_file, limit=limit)

        if excel or csv or encoding != "utf-8":
            excel_file = csv_file[:-3] + "xlsx"
            csv_file, excel_file = convert_csv_to_excel(csv_file, encoding=encoding, output_csv=csv, output_excel=excel)

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
