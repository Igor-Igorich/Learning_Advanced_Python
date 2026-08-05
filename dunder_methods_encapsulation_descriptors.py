import logging
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class HyperparameterConfig:
    """
    Производственный класс конфигурации гиперпараметров.
    
    Архитектура:
    
    1. Инкапсуляция: __learning_rate (name mangling -> _HyperparameterConfig__learning_rate)
    2. property: @property + @learning_rate.setter + @learning_rate.deleter
    3. Валидация: TypeError (не float) + ValueError (≤0 или ≥1.0)
    4. dunder: __repr__, __str__, __call__
    """
    
    _VALID_PARAMETERS = {'learning_rate', 'batch_size', 'epochs', 'optimizer'}
    
    def __init__(self, learning_rate: float = 0.001):
        logger.info("Инициализация HyperparameterConfig")
        self.learning_rate = learning_rate   # Через setter с валидацией
        self.batch_size: int = 32
        self.epochs: int = 10
        self.optimizer: str = 'adam'
    
    @property
    def learning_rate(self) -> float:
        """Геттер для чтения приватного (name-mangled) параметра __learning_rate.
        Note:
            return self.__learning_rate
              эквивалентно
            return self._HyperparameterConfig__learning_rate
        """
        return self.__learning_rate
    
    @learning_rate.setter
    def learning_rate(self, value: Any) -> None:
        """
        Сеттер: жёсткая валидация + логирование.
        
        Raises:
            TypeError:  value не является float
            ValueError: value ≤ 0 или value ≥ 1.0
        """
        logger.debug(f"Попытка установить learning_rate = {value!r}")
        
        # Валидация типа
        if not isinstance(value, float):
            error_msg = (
                f"[TypeError] learning_rate должен быть типа float, "
                f"получен {type(value).__name__} (значение: {value!r})"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        # Валидация диапазона
        if value <= 0.0:
            error_msg = f"[ValueError] learning_rate должен быть > 0.0, получено {value}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if value >= 1.0:
            error_msg = f"[ValueError] learning_rate должен быть < 1.0, получено {value}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Запись в приватный атрибут (name mangling)
        self.__learning_rate = value
        logger.info(f"learning_rate успешно установлен: {value}")
    
    @learning_rate.deleter
    def learning_rate(self) -> None:
        """Делитер: запрещает удаление."""
        raise AttributeError("[AttributeError] Удаление learning_rate запрещено")
    
    def __repr__(self) -> str:
        """Официальное представление для логов."""
        return (
            f"HyperparameterConfig("
            f"learning_rate={self.learning_rate!r}, "
            f"batch_size={self.batch_size!r}, "
            f"epochs={self.epochs!r}, "
            f"optimizer={self.optimizer!r})"
        )
    
    def __str__(self) -> str:
        """Красивое форматирование для пользователя."""
        return (
            f"╔══════════════════════════════════════╗\n"
            f"║  learning_rate : {self.learning_rate:<18.6f} ║\n"
            f"║  batch_size    : {self.batch_size:<18d} ║\n"
            f"║  epochs        : {self.epochs:<18d} ║\n"
            f"║  optimizer     : {self.optimizer:<18s} ║\n"
            f"╚══════════════════════════════════════╝"
        )
    
    def __call__(self, **kwargs: Any) -> 'HyperparameterConfig':
        """
        Динамическое обновление параметров.
        
        Пример: config(learning_rate=0.01, epochs=50)
        
        Returns:
            self — поддержка цепочки вызовов
        """
        logger.info(f"Динамическое обновление: {kwargs}")
        
        for key, value in kwargs.items():
            if key not in self._VALID_PARAMETERS:
                raise ValueError(
                    f"Неизвестный параметр '{key}'. "
                    f"Допустимые: {self._VALID_PARAMETERS}"
                )
            setattr(self, key, value)   # Через property для learning_rate!
        
        return self