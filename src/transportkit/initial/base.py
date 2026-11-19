"""Базовий клас методів побудови опорного плану та спільні допоміжні засоби."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from ..exceptions import OptimizationError
from ..problem import TransportProblem
from ..solution import TransportSolution
from ..utils import ensure_feasible, is_zero, timed

Cell = Tuple[int, int]


class Allocator:
    """Допоміжний об'єкт для методів «викреслювання ліній».

    Стежить за залишками запасів/потреб і відкритими рядками та стовпцями.
    Після кожного розподілу закривається рівно одна лінія (крім останнього кроку),
    тому в результаті завжди утворюється m + n - 1 базисних клітинок без циклів.
    """

    def __init__(self, problem: TransportProblem) -> None:
        self.problem = problem
        self.supply: List[float] = list(problem.supply)
        self.demand: List[float] = list(problem.demand)
        self.open_rows: List[int] = list(range(problem.m))
        self.open_cols: List[int] = list(range(problem.n))
        self.plan: Dict[Cell, float] = {}

    @property
    def finished(self) -> bool:
        return not self.open_rows or not self.open_cols

    def is_open(self, i: int, j: int) -> bool:
        return i in self.open_rows and j in self.open_cols

    def allocate(self, i: int, j: int, prefer: str = "row"):
        """Розподіляє max можливу кількість у клітинку (i, j) і закриває лінію.

        Якщо вичерпано і запас, і потребу одночасно, закривається лише одна лінія
        (``prefer`` — "row" або "col"); друга лишається з нульовим залишком,
        що й дає виродженість плану.
        """
        # Перевозимо менше з двох: залишок запасу або залишок потреби
        x = min(self.supply[i], self.demand[j])
        self.plan[(i, j)] = self.plan.get((i, j), 0) + x
        self.supply[i] -= x
        self.demand[j] -= x
        if is_zero(self.supply[i]):
            self.supply[i] = 0
        if is_zero(self.demand[j]):
            self.demand[j] = 0

        # Вичерпаний рядок або стовпець закриваємо (викреслюємо)
        close_row = self.supply[i] == 0
        close_col = self.demand[j] == 0
        # Якщо вичерпано обидва одразу — закриваємо лише один (це дає вироджений план)
        if close_row and close_col:
            if prefer == "row":
                if len(self.open_rows) > 1:
                    close_col = False
                elif len(self.open_cols) > 1:
                    close_row = False
            else:
                if len(self.open_cols) > 1:
                    close_row = False
                elif len(self.open_rows) > 1:
                    close_col = False
        if close_row:
            self.open_rows.remove(i)
        if close_col:
            self.open_cols.remove(j)
        return x


def complete_basis(problem: TransportProblem, plan: Dict[Cell, float]) -> Dict[Cell, float]:
    """Доповнює базис нульовими клітинками до m + n - 1, не створюючи циклів."""
    m, n = problem.m, problem.n
    # Union-Find: стежимо, щоб додані нульові клітинки не утворили цикл
    parent = list(range(m + n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    result = dict(plan)
    for (i, j) in result:
        parent[find(i)] = find(m + j)
    # Додаємо найдешевші клітинки, що з'єднують різні частини базису
    for i, j, _ in sorted(problem.cells(), key=lambda cell: (cell[2], cell[0], cell[1])):
        if len(result) >= m + n - 1:
            break
        if (i, j) not in result and find(i) != find(m + j):
            result[(i, j)] = 0
            parent[find(i)] = find(m + j)
    return result


class InitialMethod(ABC):
    """Абстрактний метод побудови початкового опорного плану.

    Шаблонний метод :meth:`solve` однаковий для всіх, а конкретний алгоритм
    підклас задає у :meth:`_build_plan` (поліморфізм).
    """

    key = "abstract"
    name = "Абстрактний метод"

    @timed
    @ensure_feasible()
    def solve(self, problem: TransportProblem) -> TransportSolution:
        # 1) закриваємо модель, 2) будуємо план, 3) доповнюємо базис до m+n-1
        work = problem.balanced()
        plan = complete_basis(work, self._build_plan(work))
        return TransportSolution(work, plan, method=self.name)

    @abstractmethod
    def _build_plan(self, problem: TransportProblem) -> Dict[Cell, float]:
        """Повертає словник базисних клітинок {(i, j): кількість}."""

    def __repr__(self) -> str:
        return f"<{type(self).__name__} key={self.key!r}>"
