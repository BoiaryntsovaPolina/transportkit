"""Клас TransportSolution — план перевезень та його характеристики."""

from __future__ import annotations

from typing import Dict, Iterator, List, Tuple

from .exceptions import TransportError
from .problem import TransportProblem
from .utils import EPS, fmt_number, is_zero, render_table

Cell = Tuple[int, int]


class TransportSolution:
    """Опорний або оптимальний план транспортної задачі.

    План зберігається як словник ``{(i, j): кількість}`` для *базисних*
    клітинок. Базисних клітинок завжди ``m + n - 1``; якщо план вироджений,
    частина з них має нульове перевезення.
    """

    def __init__(self, problem: TransportProblem, plan: Dict[Cell, float], method: str,
                 iterations: int = 0, history: List[float] = None) -> None:
        self._problem = problem
        self._plan: Dict[Cell, float] = dict(plan)
        self.method = method
        self.iterations = iterations
        self.elapsed = 0.0
        self.history: List[float] = list(history) if history else [self.total_cost]

    # ---------------------------------------------------------------- властивості
    @property
    def problem(self) -> TransportProblem:
        """Закрита (збалансована) задача, для якої побудовано план."""
        return self._problem

    @property
    def plan(self) -> Dict[Cell, float]:
        """Копія словника базисних клітинок (зовнішній код не може зіпсувати план)."""
        return dict(self._plan)

    @property
    def total_cost(self):
        """Цільова функція Z = Σ c_ij · x_ij."""
        return sum(self._problem.cost(i, j) * q for (i, j), q in self._plan.items())

    @property
    def basis_size(self) -> int:
        return len(self._plan)

    @property
    def is_degenerate(self) -> bool:
        """План вироджений, якщо серед базисних клітинок є нульові."""
        return any(is_zero(q) for q in self._plan.values())

    # ---------------------------------------------------------------- перевірка
    def check(self, tolerance: float = EPS) -> None:
        """Перевіряє допустимість плану; при порушенні піднімає TransportError."""
        p = self._problem
        if any(q < -tolerance for q in self._plan.values()):
            raise TransportError("План містить від'ємні перевезення.")
        if len(self._plan) != p.m + p.n - 1:
            raise TransportError(
                f"Кількість базисних клітинок ({len(self._plan)}) має дорівнювати m+n-1 = {p.m + p.n - 1}.")
        # Рахуємо суми перевезень по рядках і стовпцях
        rows = [0] * p.m
        cols = [0] * p.n
        for (i, j), q in self._plan.items():
            rows[i] += q
            cols[j] += q
        for i in range(p.m):
            if abs(rows[i] - p.supply[i]) > tolerance:
                raise TransportError(f"Порушено запас постачальника {p.row_label(i)}.")
        for j in range(p.n):
            if abs(cols[j] - p.demand[j]) > tolerance:
                raise TransportError(f"Порушено потребу споживача {p.col_label(j)}.")

    def is_feasible(self, tolerance: float = EPS) -> bool:
        try:
            self.check(tolerance)
        except TransportError:
            return False
        return True

    # ---------------------------------------------------------------- подання
    def matrix(self) -> List[List[float]]:
        """Повна матриця перевезень m×n (небазисні клітинки — нулі)."""
        p = self._problem
        result = [[0] * p.n for _ in range(p.m)]
        for (i, j), q in self._plan.items():
            result[i][j] = q
        return result

    def allocations(self) -> Iterator[Tuple[int, int, float]]:
        """Генератор ненульових перевезень (i, j, кількість) у порядку клітинок."""
        for (i, j) in sorted(self._plan):
            q = self._plan[(i, j)]
            if not is_zero(q):
                yield i, j, q

    def to_dict(self) -> dict:
        p = self._problem
        return {
            "method": self.method,
            "total_cost": self.total_cost,
            "iterations": self.iterations,
            "degenerate": self.is_degenerate,
            "problem": p.to_dict(),
            "allocations": [
                {"from": p.row_label(i), "to": p.col_label(j), "quantity": q}
                for i, j, q in self.allocations()
            ],
            "matrix": self.matrix(),
        }

    # ---------------------------------------------------------------- спеціальні методи
    def __iter__(self) -> Iterator[Tuple[int, int, float]]:
        return self.allocations()

    def __len__(self) -> int:
        return sum(1 for _ in self.allocations())

    def __getitem__(self, position: Cell):
        return self._plan.get(tuple(position), 0)

    def __repr__(self) -> str:
        return f"TransportSolution(method={self.method!r}, Z={fmt_number(self.total_cost)})"

    def __str__(self) -> str:
        p = self._problem
        header = [""] + [p.col_label(j) for j in range(p.n)] + ["Запаси"]
        rows = []
        for i in range(p.m):
            # «·» позначає небазисну (порожню) клітинку
            cells = [fmt_number(self._plan[(i, j)]) if (i, j) in self._plan else "·" for j in range(p.n)]
            rows.append([p.row_label(i)] + cells + [fmt_number(p.supply[i])])
        rows.append(["Потреби"] + [fmt_number(d) for d in p.demand] + [fmt_number(p.total_demand)])
        lines = [f"Метод: {self.method}", render_table(header, rows),
                 f"Z = {fmt_number(self.total_cost)}"]
        if self.iterations:
            lines[-1] += f"  (ітерацій оптимізації: {self.iterations})"
        if self.is_degenerate:
            lines.append("Увага: план вироджений (є базисні клітинки з нульовим перевезенням).")
        return "\n".join(lines)
