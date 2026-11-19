"""Високорівневий інтерфейс: реєстр методів, solve() і compare_methods()."""

from __future__ import annotations

from typing import Dict, Iterator, List, Union

from .exceptions import UnknownMethodError
from .initial import (DoublePreference, InitialMethod, MinCostByColumn, MinCostByRow,
                      MinCostByTable, NorthEastCorner, NorthWestCorner, SouthEastCorner,
                      SouthWestCorner, Vogel)
from .optimization import PotentialsMethod
from .problem import TransportProblem
from .solution import TransportSolution

#: Реєстр методів: ключ → екземпляр.
METHODS: Dict[str, InitialMethod] = {
    method.key: method
    for method in (NorthWestCorner(), NorthEastCorner(), SouthWestCorner(), SouthEastCorner(),
                   MinCostByRow(), MinCostByColumn(), MinCostByTable(),
                   DoublePreference(), Vogel())
}


def available_methods() -> List[str]:
    """Список ключів доступних методів побудови опорного плану."""
    return list(METHODS)


def solve(problem: TransportProblem, method: Union[str, InitialMethod] = "vogel",
          optimize: bool = True) -> TransportSolution:
    """Розв'язує транспортну задачу.

    ``method`` — ключ із :data:`METHODS` або власний об'єкт-нащадок InitialMethod.
    Якщо ``optimize=True``, опорний план покращується методом потенціалів.
    """
    if isinstance(method, str):
        try:
            method = METHODS[method]
        except KeyError:
            raise UnknownMethodError(
                f"Невідомий метод {method!r}. Доступні: {', '.join(METHODS)}.") from None
    # Спочатку опорний план, потім (за потреби) оптимізація
    solution = method.solve(problem)
    return PotentialsMethod().optimize(solution) if optimize else solution


def compare_methods(problem: TransportProblem, optimize: bool = False) -> Iterator[TransportSolution]:
    """Генератор: по черзі розв'язує задачу всіма методами."""
    for key in METHODS:
        yield solve(problem, key, optimize=optimize)
