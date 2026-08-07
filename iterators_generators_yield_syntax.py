
# def process(x: int) -> None:
#     print (f"Было получено значение: {x}")

# sequence = [i for i in range(5)]

# Когда мы пишем:
# for item in sequence:
#     process(item)

# Интерпретатор CPython преобразует этот код в эквивалентный цикл:
# _iterator = iter(sequence)  # Вызывает sequence.__iter__()
# while True:
#     try:
#         item = next(_iterator)  # Вызывает _iterator.__next__()
#     except StopIteration:
#         break
#     process(item)

# class FibonacciIterator:
#     def __init__(self, limit: int):
#         self.limit = limit
#         self.count = 0
#         self.a, self.b = 0, 1

#     def __iter__(self):
#         # Итератор возвращает сам себя
#         return self

#     def __next__(self) -> int:
        
#         if self.count >= self.limit:
#             raise StopIteration
        
#         result = self.a
#         self.a, self.b = self.b, self.a + self.b
#         self.count += 1
#         return result

# fib = FibonacciIterator(5)
# for num in fib:
#     print(num)  # Выведет: 0, 1, 1, 2, 3

# def simple_gen():
#     yield 1
#     yield 2

# g = simple_gen()
# print(type(g))  # <class 'generator'>

# import sys

# # List comprehension (Eager Evaluation / Жадные вычисления)
# large_list = [x for x in range(10_000_000)]
# print(f"Память списка: {sys.getsizeof(large_list) / (1024 * 1024):.2f} MB") # ~85 MB

# # Generator expression (Lazy Evaluation / Ленивые вычисления)
# large_gen = (x for x in range(10_000_000))
# print(f"Память генератора: {sys.getsizeof(large_gen)} bytes") # 200 bytes

# def consumer():
#     print("Старт сопрограммы")
#     while True:
#         received = yield
#         print(f"Получено значение: {received}")

# c = consumer()
# next(c)        # Первоначальный «разогрев» (advance to first yield)
# c.send("Test") # Выведет: Получено значение: Test
# c.send(5) # Выведет: Получено значение: Test
# c.send(10.0) # Выведет: Получено значение: Test
# c.close()


# def subgenerator():
#     yield 1
#     yield 2

# def main_generator():
#     yield "Start"
#     yield from subgenerator()  # Делегирование обхода
#     yield "End"

# print(list(main_generator()))  # ['Start', 1, 2, 'End']


# def fib_gen():
#     a = 0
#     b = 1
#     while True:
#         yield a
#         a, b = b, a + b

# gen = fib_gen()

# for _ in range(10):
#     print(next(gen), end=" ")

# Оператор yield не разрешён в блоке try конструкции try/finally.
# Сложность в том, что нет гарантии, что генератор когда-либо будет возобновлён,
# следовательно, нет гарантии, что блок finally когда-либо будет выполнен;
# это слишком сильное нарушение назначения finally.


# def read_large_file(filepath):
#     """Лениво читает файл по строкам."""
#     with open(filepath, 'r') as f:
#         for line in f:
#             yield line.strip()

# def filter_comments(lines):
#     """Фильтрует строки-комментарии."""
#     for line in lines:
#         if not line.startswith('#'):
#             yield line

# def parse_records(lines):
#     """Парсит строки в записи."""
#     for line in lines:
#         yield line.split(',')

# # Конвейер: каждый этап обрабатывает одну строку за раз
# pipeline = parse_records(filter_comments(read_large_file('data.csv')))

# for record in pipeline:
#     process(record)  # Память O(1) вне зависимости от размера файла


import sys
import random
import os
from datetime import datetime, timedelta

file_path = "large_backend_clicks.log"
num_lines = 100_000

start_time = datetime(2026, 8, 1, 0, 0, 0)

status_codes = [200, 200, 200, 200, 200, 200, 200, 200, 500, 500] # Доля 500 составляет ~20%
'''
with open(file_path, "w", encoding="utf-8") as f:
    for i in range(num_lines):
        ts = (start_time + timedelta(seconds=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        user_id = random.randint(1000, 9999)
        status = random.choice(status_codes)
        latency = random.randint(10, 500)
        f.write(f"{ts},{user_id},{status},{latency}\n")

file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
print(f"Файл создан успешно. Размер файла на диске: {file_size_mb:.2f} МБ\n")
'''


    
def read_log_file(filepath: str):
    """Лениво читает файл, очищает строки и пропускает пустые."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Пропускаем пустые строки сразу
                yield line

def parse_log_records(lines):
    """Парсит строки формата CSV в словари."""
    for line in lines:
        parts = line.split(",")
        if len(parts) == 4:
            timestamp, user_id, status_code, latency = parts
            yield {
                "timestamp": timestamp,
                "user_id": int(user_id),
                "status_code": int(status_code),
                "latency": int(latency)
            }

def filter_errors(records, target_status=500):
    """Фильтрует записи по коду статуса."""
    for record in records:
        if record["status_code"] == target_status:
                yield record
    

pipeline = filter_errors(parse_log_records(read_log_file(file_path)), target_status=500)


size_initial = sys.getsizeof(pipeline)
print(f"Размер объекта-пайплайна до итерации: {size_initial} байт")

count_500 = 0
sample_logs = []

for log in pipeline:
    count_500 += 1
    if count_500 <= 3:
        sample_logs.append(log)
    # Периодически выводим объем памяти самого генератора в процессе итерации
    if count_500 % 5000 == 0:
        print(f"Обработано {count_500} ошибок 500 | Текущий размер пайплайна: {sys.getsizeof(pipeline)} байт")

size_final = sys.getsizeof(pipeline)
print(f"Размер объекта-пайплайна после полной обработки: {size_final} байт")

print(f"\nВсего найдено строк с ошибкой 500: {count_500:,}")
print("\nПример первых 3 распарсенных записей 500:")
for log in sample_logs:
    print(" ", log)


def log_stream_reader(file_path: str):
    """
    Лениво читает файл логов строка за строкой, парсит её в словарь
    и с помощью yield выдает только те записи, у которых status_code == '500'.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) == 4:
                timestamp, user_id, status_code, latency = parts
                if status_code == '500':
                    yield {
                        "timestamp": timestamp,
                        "user_id": int(user_id),
                        "status_code": int(status_code),
                        "latency": int(latency)
                    }



gen = log_stream_reader(file_path)

size_initial = sys.getsizeof(gen)
print(f"Размер объекта-генератора до итерации: {size_initial} байт")

count_500 = 0
sample_logs = []

for log in gen:
    count_500 += 1
    if count_500 <= 3:
        sample_logs.append(log)
    # Периодически выводим объем памяти самого генератора в процессе итерации
    if count_500 % 5000 == 0:
        print(f"Обработано {count_500} ошибок 500 | Текущий размер генератора: {sys.getsizeof(gen)} байт")

size_final = sys.getsizeof(gen)
print(f"Размер объекта-генератора после полной обработки: {size_final} байт")

print(f"\nВсего найдено строк с ошибкой 500: {count_500:,}")
print("\nПример первых 3 распарсенных записей 500:")
for log in sample_logs:
    print(" ", log)