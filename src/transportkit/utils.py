"""Допоміжні засоби: допуск порівняння, таймер (контекстний менеджер), декоратори, форматування."""

from __future__ import annotations

import functools
import time

from .exceptions import TransportError

#: Допуск для порівняння дійсних чисел з нулем.
EPS = 1e-9


def is_zero(value, tolerance: float = EPS) -> bool:
    """Повертає True, якщо число за модулем не перевищує допуск."""
    return abs(value) <= tolerance


def fmt_number(value) -> str:
    """Форматує число: ціле без «.0», дійсне — до 4 значущих знаків."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4g}"
    return str(value)


def render_table(header, rows) -> str:
    """Будує текстову таблицю з вирівняними стовпцями.

    Перший стовпець вирівнюється вліво, інші — вправо.
    """
    table = [[str(x) for x in row] for row in [list(header)] + [list(r) for r in rows]]
    widths = [max(len(row[c]) for row in table) for c in range(len(header))]
    lines = []
    for k, row in enumerate(table):
        parts = [row[0].ljust(widths[0])]
        parts += [row[c].rjust(widths[c]) for c in range(1, len(row))]
        lines.append(" | ".join(parts))
        if k == 0:
            lines.append("-+-".join("-" * w for w in widths))
    return "\n".join(lines)


class Stopwatch:
    """Контекстний менеджер, що вимірює час виконання блоку коду.

    >>> with Stopwatch() as sw:
    ...     sum(range(1000))
    499500
    >>> sw.elapsed >= 0
    True
    """

    def __init__(self) -> None:
        self.elapsed = 0.0
        self._start = 0.0

    def __enter__(self) -> "Stopwatch":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.elapsed = time.perf_counter() - self._start
        return False  # винятки не «ковтаємо»


def timed(func):
    """Декоратор: записує час роботи функції в атрибут ``elapsed`` результату."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Вимірюємо час виконання функції
        with Stopwatch() as watch:
            result = func(*args, **kwargs)
        if hasattr(result, "elapsed"):
            result.elapsed = watch.elapsed
        return result

    return wrapper


def ensure_feasible(tolerance: float = EPS):
    """Декоратор з параметром: перевіряє допустимість розв'язку, який повертає функція.

    Якщо план порушує баланс запасів або потреб, виникає ``TransportError``.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result.check(tolerance)
            return result

        return wrapper

    return decorator


__all__ = ["EPS", "is_zero", "fmt_number", "render_table", "Stopwatch", "timed",
           "ensure_feasible", "TransportError"]
