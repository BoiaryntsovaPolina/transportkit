"""Методи кутів: північно-західний, північно-східний, південно-західний, південно-східний."""

from __future__ import annotations

from ..utils import is_zero
from .base import InitialMethod


class CornerMethod(InitialMethod):
    """Загальний алгоритм «кутового» методу.

    Старт — із заданого кута таблиці, рух по «сходинках» до протилежного кута.
    Напрямок руху задають атрибути ``row_step`` і ``col_step`` (+1 або -1).
    """

    row_step = 1
    col_step = 1

    def _build_plan(self, problem):
        m, n = problem.m, problem.n
        # Стартова клітинка — потрібний кут таблиці
        i = 0 if self.row_step > 0 else m - 1
        j = 0 if self.col_step > 0 else n - 1
        last_i = m - 1 if self.row_step > 0 else 0
        last_j = n - 1 if self.col_step > 0 else 0
        supply, demand = list(problem.supply), list(problem.demand)
        plan = {}
        # Рухаємось «сходинками» до протилежного кута
        while True:
            # Розподіляємо максимально можливу кількість
            x = min(supply[i], demand[j])
            plan[(i, j)] = x
            supply[i] -= x
            demand[j] -= x
            if is_zero(supply[i]):
                supply[i] = 0
            if is_zero(demand[j]):
                demand[j] = 0
            if i == last_i and j == last_j:
                break
            # Запас вичерпано — переходимо до наступного рядка, інакше — до наступного стовпця
            if supply[i] == 0 and i != last_i:
                i += self.row_step
            elif j != last_j:
                j += self.col_step
            else:
                i += self.row_step
        return plan


class NorthWestCorner(CornerMethod):
    key, name = "nw", "Північно-західного кута"
    row_step, col_step = 1, 1


class NorthEastCorner(CornerMethod):
    key, name = "ne", "Північно-східного кута"
    row_step, col_step = 1, -1


class SouthWestCorner(CornerMethod):
    key, name = "sw", "Південно-західного кута"
    row_step, col_step = -1, 1


class SouthEastCorner(CornerMethod):
    key, name = "se", "Південно-східного кута"
    row_step, col_step = -1, -1
