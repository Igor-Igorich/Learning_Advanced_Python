import functools
import logging
import os
import random
import sys
import time
from typing import Any, Dict, Iterator, Tuple

from log_file_generator import generate_sample_log_file

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def benchmark(func):
    """Декоратор для точного измерения времени выполнения функций.

    Notes:
        Использует time.perf_counter() для высокой точности,
        поддерживает произвольные аргументы и сохраняет метаданные через @functools.wraps.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logger.info(f"Начало выполнения функции '{func.__name__}'...")

        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        logger.info(
            f"Функция '{func.__name__}' выполнена за {execution_time:.4f} секунд."
        )
        return result

    return wrapper


# примитивная функция
'''
def parse_server_logs(file_path: str):
    """
    Ленивый генератор, читающий файл построчно (O(1) по памяти).

    Бизнес-логика:
    Отфильтровывает на лету и отдаёт наружу только строки, где:
      - HTTP Status == 500 или 503 (ошибка сервера)
      ИЛИ
      - Latency > 500 мс (критический порог)

    Возвращает данные в виде структурированного словаря.
    """

    with open(file_path, "w", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) != 6:
                    continue

                timestamp, ip, method, endpoint, status_str, latency_str = parts
                status = int(status)
                latency = int(latency)

                if status in (500, 503) or latency > 500:
                    yield {
                        "line_num": line_num,
                        "timestamp": timestamp,
                        "ip": ip,
                        "method": method,
                        "endpoint": endpoint,
                        "status": status,
                        "latency_ms": latency,
                    }
            except (ValueError, IndexError):
                # Игнорируем повреждённые строки
                continue
'''


def read_log_file(file_path: str) -> Iterator[Tuple[int, str]]:
    """Лениво читает файл, очищает строки и пропускает пустые."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                yield line_num, line

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Ошибка чтения файла: {e}")
        raise


def parse_log_records(
    lines: Iterator[Tuple[int, str]],
) -> Iterator[Dict[str, Any]]:
    """Парсит строки формата CSV в словари."""

    for line_num, line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 6:
            logger.warning(f"Строка {line_num}: Неверный формат: {line}")
            continue

        try:
            timestamp, ip, method, endpoint, status_str, latency_str = parts
            status = int(status_str)
            latency = int(latency_str)
            yield {
                "line_num": line_num,
                "timestamp": timestamp,
                "ip": ip,
                "method": method,
                "endpoint": endpoint,
                "status": status,
                "latency_ms": latency,
            }
        except ValueError as e:
            logger.warning(f"Строка {line_num}: Ошибка преобразования: {e}")
            continue


def filter_errors(
    records: Iterator[Dict[str, Any]],
) -> Iterator[Dict[str, Any]]:
    """Фильтрует записи по коду статуса."""
    for record in records:
        if record["status"] in (500, 503) or record["latency_ms"] > 500:
            yield record


def create_log_pipeline(file_path: str) -> Iterator[Dict[str, Any]]:
    return filter_errors(parse_log_records(read_log_file(file_path)))


@benchmark
def process_logs_pipeline(file_path: str) -> None:
    """
    Облачает вызов генератора в цикл и обрабатывает n сгенерированных строк.
    Доказывает O(1) потребление памяти через sys.getsizeof().
    """

    log_generator = create_log_pipeline(file_path)

    gen_size = sys.getsizeof(log_generator)
    logger.info(
        f"[Контроль памяти] Размер объекта-генератора log_generator в RAM: {gen_size} байт"
    )

    total_processed = 0
    anomalies_found = 0

    for item in log_generator:
        anomalies_found += 1
        total_processed = item["line_num"]

        if anomalies_found % 30000 == 1:
            item_size = sys.getsizeof(item)
            logger.info(
                f"[Контроль памяти] Аномалия #{anomalies_found:,} (строка файла #{total_processed:,}): "
                f"размер текущего объекта = {item_size} байт. Память = O(1) константа."
            )

    logger.info("Обработка полностью завершена.")
    logger.info(f"Всего обработано строк из файла: {total_processed:,}")
    logger.info(
        f"Найдено аномальных записей (500/503 или latency > 500ms): {anomalies_found:,}"
    )


def main() -> None:
    """Точка входа в программу."""

    LOG_FILE = "api_server_logs.txt"

    generate_sample_log_file(LOG_FILE, num_lines=150_000)

    process_logs_pipeline(LOG_FILE)

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        logger.info(
            f"Тестовый файл '{LOG_FILE}' успешно удален после завершения теста."
        )


if __name__ == "__main__":
    main()
