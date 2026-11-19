"""Метод апроксимації Фогеля."""

from __future__ import annotations

from .base import Allocator, InitialMethod


class Vogel(InitialMethod):
    """Метод Фогеля.

    На кожному кроці для кожного відкритого рядка і стовпця обчислюється штраф —
    різниця двох найменших вартостей. Обирається лінія з найбільшим штрафом
    (при рівності — рядок раніше за стовпець, далі менший індекс), у ній —
    клітинка з найменшою вартістю.
    """

    key, name = "vogel", "Фогеля"

    @staticmethod
    def penalty(values):
        values = sorted(values)
        return values[0] if len(values) == 1 else values[1] - values[0]

    def _build_plan(self, problem):
        allocator = Allocator(problem)
        while not allocator.finished:
            # Штраф лінії = різниця двох її найменших вартостей
            lines = []
            for i in allocator.open_rows:
                pen = self.penalty([problem.cost(i, j) for j in allocator.open_cols])
                lines.append((-pen, 0, i))
            for j in allocator.open_cols:
                pen = self.penalty([problem.cost(i, j) for i in allocator.open_rows])
                lines.append((-pen, 1, j))
            # Мінус перед штрафом: min() знаходить лінію з найбільшим штрафом
            _, kind, index = min(lines)
            if kind == 0:
                i = index
                j = min(allocator.open_cols, key=lambda col: (problem.cost(i, col), col))
            else:
                j = index
                i = min(allocator.open_rows, key=lambda row: (problem.cost(row, j), row))
            allocator.allocate(i, j)
        return allocator.plan
