import csv
import os
from datetime import datetime

DOWNLOADS_DIR = "downloads"


def create_csv_file(filename_suffix: str = "aave", filename: str = "", headers: list = [], delimiter: str = ",") -> str:
    """
    Функция создает новый CSV-файл с заданными параметрами и возвращает путь к созданному файлу.

    Аргументы:
     - `filename_suffix`: `str` (по умолчанию "aave") - суффикс для названия файла.
     - `filename`: `str` (по умолчанию "") - название файла. Если не указано, то имя файла генерируется автоматически.
     - `headers`: `list` (по умолчанию []) - список заголовков. Если не указан, то заголовок не записывается в файл.
     - `delimiter`: `str` (по умолчанию ",") - разделитель, который будет использоваться в CSV-файле.

    Возвращает путь к созданному файлу.

    Исключения:
    - `OSError`: при ошибке создания директории или файла.
    """
    if not filename:
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename_suffix}.csv"

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOADS_DIR, filename)

    try:
        with open(file_path, "w", newline="") as file:
            if headers:
                writer = csv.writer(file, delimiter=delimiter)
                writer.writerow(headers)
    except OSError as e:
        raise OSError(f"Ошибка при создании файла: {e}")

    return os.path.abspath(file_path)
