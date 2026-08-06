
import functools
import logging
import time
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)



def benchmark(func):
    """
    Декоратор для точного измерения времени выполнения функций.
    
    Использует time.perf_counter() для высокой точности,
    поддерживает произвольные аргументы и сохраняет метаданные через @functools.wraps.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.debug(
            f"Функция {func.__name__} выполнилась за {execution_time:.4f} секунд."
        )
        return result
    return wrapper


@benchmark
def train_logistic_regression(
    model: LogisticRegression, 
    X_train: pd.DataFrame, 
    y_train: pd.Series
) -> LogisticRegression:
    """Выполняет шаг обучения модели LogisticRegression."""
    return model.fit(X_train, y_train)


def generate_imbalanced_data(
    n_samples: int = 5000,
    n_features: int = 10,
    weights: List[float] = [0.95, 0.05],
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.Series]:
    if n_samples <= 0:
        raise ValueError("Параметр n_samples должен быть строго больше 0.")
    if not np.isclose(sum(weights), 1.0):
        raise ValueError("Сумма элементов массива weights должна быть равна 1.0.")
    
    X_raw, y_raw = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        weights=weights,
        random_state=seed
    )
    
    feature_names = [f"feature_{i}" for i in range(n_features)]
    X = pd.DataFrame(X_raw, columns=feature_names)
    y = pd.Series(y_raw, name="target")
    
    return X, y


def calculate_manual_metrics(
    tn: int,
    fp: int,
    fn: int,
    tp: int
) -> Dict[str, float]:
    total = tp + tn + fp + fn
    if total == 0:
        raise ZeroDivisionError("Общая сумма элементов матрицы ошибок равна 0.")
    
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn)
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def main() -> None:
    rnd_seed = 42
    
    logger.info("Генерация синтетического несбалансированного датасета...")
    X, y = generate_imbalanced_data(
        n_samples=50_000,
        n_features=10,
        weights=[0.95, 0.05],
        seed=rnd_seed
    )

    class_distribution = y.value_counts(normalize=True) * 100
    logger.info(
        f"Распределение классов (%):\n{class_distribution.to_string()}"
    )
    
    logger.info("Разделение выборки на обучающую и тестовую (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=rnd_seed,
        stratify=y
    )
    
    logger.info("Обучение модели LogisticRegression...")
    model = LogisticRegression(random_state=rnd_seed, max_iter=1000)
    
    train_logistic_regression(model, X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    logger.info("Вычисление метрик с помощью библиотечных функций scikit-learn...")
    cm_sklearn = confusion_matrix(y_test, y_pred)
    acc_sklearn = accuracy_score(y_test, y_pred)
    prec_sklearn = precision_score(y_test, y_pred, zero_division=0)
    rec_sklearn = recall_score(y_test, y_pred, zero_division=0)
    f1_sklearn = f1_score(y_test, y_pred, zero_division=0)
    
    logger.info("\n--- Библиотечные метрики (Scikit-Learn) ---")
    logger.info(f"Confusion Matrix:\n{cm_sklearn}")
    logger.info(f"Accuracy:  {acc_sklearn:.6f}")
    logger.info(f"Precision: {prec_sklearn:.6f}")
    logger.info(f"Recall:    {rec_sklearn:.6f}")
    logger.info(f"F1-score:  {f1_sklearn:.6f}")
    
    logger.info("\nВычисление метрик кастомной функцией...")
    tn, fp, fn, tp = cm_sklearn.ravel()
    logger.info(f"Компоненты матрицы ошибок: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    
    manual_metrics = calculate_manual_metrics(tn=tn, fp=fp, fn=fn, tp=tp)

    logger.info("\n--- Результаты ручного расчета ---")
    logger.info(f"Accuracy:  {manual_metrics['accuracy']:.6f}")
    logger.info(f"Precision: {manual_metrics['precision']:.6f}")
    logger.info(f"Recall:    {manual_metrics['recall']:.6f}")
    logger.info(f"F1-score:  {manual_metrics['f1_score']:.6f}")
    
    logger.info("\nСверка результатов (Sklearn vs Manual):")
    is_acc_match = np.isclose(acc_sklearn, manual_metrics["accuracy"])
    is_prec_match = np.isclose(prec_sklearn, manual_metrics["precision"])
    is_rec_match = np.isclose(rec_sklearn, manual_metrics["recall"])
    is_f1_match = np.isclose(f1_sklearn, manual_metrics["f1_score"])

    if all([is_acc_match, is_prec_match, is_rec_match, is_f1_match]):
        logger.info("УСПЕХ: Все ручные метрики полностью совпадают с библиотечными!")
    else:
        logger.error("ОШИБКА: Обнаружены расхождения в расчетах!")


if __name__ == "__main__":
    main()