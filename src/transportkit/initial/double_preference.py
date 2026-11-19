"""Метод подвійної переваги."""

from __future__ import annotations

from .base import Allocator, InitialMethod


class DoublePreference(InitialMethod):
    """Метод подвійної переваги.

    1. У кожному рядку та стовпці позначається клітинка з мінімальною вартістю
       (при рівних вартостях — перша за індексом).
    2. Спочатку заповнюються клітинки з двома позначками (за зростанням вартості),
    3. потім з однією позначкою,
    4. і нарешті решта — за методом мінімальної вартості.
    """

    key, name = "double", "Подвійної переваги"

    @staticmethod
    def marks(problem):
        """Повертає словник {(i, j): кількість позначок 0..2}."""
        # Для кожної клітинки рахуємо, скільки разів її позначено мінімумом
        count = {(i, j): 0 for i, j, _ in problem.cells()}
        for i in range(problem.m):
            j = min(range(problem.n), key=lambda col: (problem.cost(i, col), col))
            count[(i, j)] += 1
        for j in range(problem.n):
            i = min(range(problem.m), key=lambda row: (problem.cost(row, j), row))
            count[(i, j)] += 1
        return count

    def _build_plan(self, problem):
        # Порядок: спочатку клітинки з двома позначками, потім з однією, потім решта
        count = self.marks(problem)
        order = sorted(problem.cells(), key=lambda c: (-count[(c[0], c[1])], c[2], c[0], c[1]))
        allocator = Allocator(problem)
        for i, j, _ in order:
            if allocator.finished:
                break
            if allocator.is_open(i, j):
                allocator.allocate(i, j)
        return allocator.plan
