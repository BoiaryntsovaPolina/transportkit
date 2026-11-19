"""Власні винятки бібліотеки transportkit."""


class TransportError(Exception):
    """Базовий виняток бібліотеки. Усі інші винятки успадковуються від нього."""


class InvalidProblemError(TransportError, ValueError):
    """Некоректні вхідні дані транспортної задачі (розмірність, типи, від'ємні запаси)."""


class UnknownMethodError(TransportError, ValueError):
    """Запитано метод, якого немає в реєстрі методів."""


class OptimizationError(TransportError):
    """Помилка під час оптимізації (вироджений базис, перевищено ліміт ітерацій)."""


class InvalidFileFormatError(TransportError):
    """JSON-файл має неправильну структуру або пошкоджений."""
