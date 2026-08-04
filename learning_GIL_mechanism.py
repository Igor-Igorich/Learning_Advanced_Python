import os
import time
import threading
import multiprocessing


N_LIMIT = 20_000_000

def cpu_bound_task(n: int) -> int:
    """Вычисление суммы квадратов чисел от 1 до n."""
    
    total = 0
    for i in range(1, n + 1):
        total += i * i
        
    return total

def run_sequential() -> float:
    
    start_time = time.perf_counter()
    
    cpu_bound_task(N_LIMIT)
    cpu_bound_task(N_LIMIT)
    
    end_time = time.perf_counter()
    
    return end_time - start_time

def run_threads() -> float:
    t1 = threading.Thread(target=cpu_bound_task, args=(N_LIMIT,))
    t2 = threading.Thread(target=cpu_bound_task, args=(N_LIMIT,))
    
    start_time = time.perf_counter()
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    end_time = time.perf_counter()
    
    return end_time - start_time

def run_processes() -> float:
    p1 = multiprocessing.Process(target=cpu_bound_task, args=(N_LIMIT,))
    p2 = multiprocessing.Process(target=cpu_bound_task, args=(N_LIMIT,))
    
    start_time = time.perf_counter()
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    end_time = time.perf_counter()
    
    return end_time - start_time

def print_results(t_seq: float, t_thr: float, t_proc: float):
    cpu_count = os.cpu_count() or 1
    
    # Расчет метрик для threading
    s_thr = t_seq / t_thr
    e_thr = (s_thr / 2) * 100
    
    # Расчет метрик для multiprocessing
    s_proc = t_seq / t_proc
    e_proc = (s_proc / 2) * 100

    print("\n" + "=" * 85)
    print(f" РЕЗУЛЬТАТЫ БЕНЧМАРКА GIL (Доступно ядер CPU: {cpu_count})")
    print("=" * 85)
    
    header = f"| {'Режим выполнения':<25} | {'Время (сек)':<12} | {'Ускорение (x)':<14} | {'Эффективность (%)':<17} |"
    divider = "+" + "-" * 27 + "+" + "-" * 14 + "+" + "-" * 16 + "+" + "-" * 19 + "+"
    
    print(divider)
    print(header)
    print(divider)
    print(f"| {'Последовательно (1 thread)':<25} | {t_seq:<12.4f} | {1.00:<14.2f} | {50.00:<17.2f} |")
    print(f"| {'Threading (2 threads)':<25} | {t_thr:<12.4f} | {s_thr:<14.2f} | {e_thr:<17.2f} |")
    print(f"| {'Multiprocessing (2 procs)':<25} | {t_proc:<12.4f} | {s_proc:<14.2f} | {e_proc:<17.2f} |")
    print(divider)
    
    print("\nАНАЛИЗ И ВЫВОДЫ:")
    print("-" * 85)
    print("1. Threading (Многопоточность):")
    if t_thr >= t_seq * 0.95:
        print(f"   Ускорение отсутствует (Время ~{t_thr:.2f}s vs {t_seq:.2f}s).")
        print("   Причина: Оба потока исполняют байткод CPython. GIL позволяет одновременно")
        print("   работать только ОДНОМУ потоку. Возникают накладные расходы на борьбу за GIL")
        print("   и переключение контекста операционной системой.")
    
    print("\n2. Multiprocessing (Многопроцессность):")
    if s_proc > 1.3:
        print(f"   Получено кратное ускорение (в {s_proc:.2f}x раз на 2 ядрах).")
        print("   Причина: Порожденные процессы имеют изолированные адресные пространства,")
        print("   собственные экземпляры CPython и независимые GIL, что обеспечивает")
        print("   настоящий физический параллелизм на уровне ядер CPU.")
    print("=" * 85 + "\n")

if __name__ == "__main__":
    print(f"Запуск бенчмарка (N = {N_LIMIT:,} итераций)...")
    
    # 1. Последовательный запуск
    t_seq = run_sequential()
    
    # 2. Многопоточный запуск
    t_thr = run_threads()
    
    # 3. Многопроцессный запуск
    t_proc = run_processes()
    
    # Вывод результатов
    print_results(t_seq, t_thr, t_proc)