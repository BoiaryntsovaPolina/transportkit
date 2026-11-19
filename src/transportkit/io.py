"""Збереження та завантаження задач і розв'язків у форматі JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .exceptions import InvalidFileFormatError
from .problem import TransportProblem
from .solution import TransportSolution

PathLike = Union[str, Path]


def save_problem(problem: TransportProblem, path: PathLike) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(problem.to_dict(), file, ensure_ascii=False, indent=2)


def load_problem(path: PathLike) -> TransportProblem:
    """Читає задачу з JSON. Структурні помилки перетворюються на InvalidFileFormatError."""
    # Помилки JSON перетворюємо на власний виняток
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise InvalidFileFormatError(f"Файл {path} не є коректним JSON: {exc}") from exc
    try:
        return TransportProblem.from_dict(data)
    except (KeyError, TypeError) as exc:
        raise InvalidFileFormatError(f"У файлі {path} немає потрібних полів: {exc!r}") from exc


def save_solution(solution: TransportSolution, path: PathLike) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(solution.to_dict(), file, ensure_ascii=False, indent=2)
