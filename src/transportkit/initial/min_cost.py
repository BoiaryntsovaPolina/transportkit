"""Методи мінімальної вартості: за рядком, за стовпцем, за всією таблицею."""

from __future__ import annotations

from abc import abstractmethod

from .base import Allocator, InitialMethod


class MinCostMethod(InitialMethod):
    """Спільний цикл: вибрати клітинку (``_pick``) → розподілити → закрити лінію."""

    prefer = "row"

    def _build_plan(self, problem):
        allocator = Allocator(problem)
        # Поки є незакреслені лінії: обираємо клітинку і розподіляємо вантаж
        while not allocator.finished:
            i, j = self._pick(problem, allocator)
            allocator.allocate(i, j, prefer=self.prefer)
        return allocator.plan

    @abstractmethod
    def _pick(self, problem, allocator):
        """Повертає наступну клітинку (i, j)."""


class MinCostByRow(MinCostMethod):
    """У поточному (першому відкритому) рядку обирається найдешевша клітинка."""

    key, name, prefer = "min_row", "Мінімальної вартості за рядком", "row"

    def _pick(self, problem, allocator):
        i = allocator.open_rows[0]
        j = min(allocator.open_cols, key=lambda col: (problem.cost(i, col), col))
        return i, j


class MinCostByColumn(MinCostMethod):
    """У поточному (першому відкритому) стовпці обирається найдешевша клітинка."""

    key, name, prefer = "min_col", "Мінімальної вартості за стовпцем", "col"

    def _pick(self, problem, allocator):
        j = allocator.open_cols[0]
        i = min(allocator.open_rows, key=lambda row: (problem.cost(row, j), row))
        return i, j


class MinCostByTable(MinCostMethod):
    """Обирається найдешевша клітинка з усіх незакреслених."""

    key, name = "min_table", "Мінімальної вартості за таблицею"

    def _pick(self, problem, allocator):
        cells = ((problem.cost(i, j), i, j) for i in allocator.open_rows for j in allocator.open_cols)
        _, i, j = min(cells)
        return i, j
