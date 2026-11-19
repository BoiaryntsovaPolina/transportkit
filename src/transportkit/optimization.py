"""Метод потенціалів (MODI) для покращення опорного плану до оптимального."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Tuple

from .exceptions import OptimizationError
from .solution import TransportSolution
from .utils import EPS, ensure_feasible, is_zero, timed

Cell = Tuple[int, int]


class PotentialsMethod:
    """Метод потенціалів.

    Алгоритм (задача на мінімум):
      1. знайти потенціали u_i, v_j з рівнянь u_i + v_j = c_ij для базисних клітинок;
      2. обчислити оцінки Δ_ij = c_ij - u_i - v_j для небазисних клітинок;
      3. якщо всі Δ_ij ≥ 0 — план оптимальний;
      4. інакше обрати клітинку з найменшою Δ, побудувати цикл, перерозподілити
         θ = min x по клітинках зі знаком «−» і повторити.
    """

    name = "Метод потенціалів"

    def __init__(self, max_iterations: int = 1000) -> None:
        self.max_iterations = max_iterations

    # ------------------------------------------------------------ головна процедура
    @timed
    @ensure_feasible()
    def optimize(self, solution: TransportSolution) -> TransportSolution:
        problem = solution.problem
        plan = solution.plan
        history = [solution.total_cost]
        for step in range(self.max_iterations + 1):
            # 1) потенціали, 2) оцінки; якщо всі ≥ 0 — оптимум, інакше перерозподіл
            u, v = self.potentials(problem, plan)
            entering = self._entering_cell(problem, plan, u, v)
            if entering is None:
                return TransportSolution(problem, plan, f"{solution.method} + потенціали",
                                         iterations=step, history=history)
            self._shift(plan, entering)
            history.append(sum(problem.cost(i, j) * q for (i, j), q in plan.items()))
        raise OptimizationError(f"Перевищено ліміт ітерацій ({self.max_iterations}).")

    # ------------------------------------------------------------ кроки алгоритму
    @staticmethod
    def potentials(problem, plan: Dict[Cell, float]):
        """Обчислює потенціали, обходячи дерево базисних клітинок."""
        u: List = [None] * problem.m
        v: List = [None] * problem.n
        by_row: Dict[int, List[int]] = {}
        by_col: Dict[int, List[int]] = {}
        for (i, j) in plan:
            by_row.setdefault(i, []).append(j)
            by_col.setdefault(j, []).append(i)
        # Один потенціал беремо довільно (0), решту знаходимо обходом дерева базису
        u[0] = 0
        stack = [("r", 0)]
        while stack:
            kind, k = stack.pop()
            if kind == "r":
                for j in by_row.get(k, []):
                    if v[j] is None:
                        v[j] = problem.cost(k, j) - u[k]
                        stack.append(("c", j))
            else:
                for i in by_col.get(k, []):
                    if u[i] is None:
                        u[i] = problem.cost(i, k) - v[k]
                        stack.append(("r", i))
        if any(x is None for x in u) or any(x is None for x in v):
            raise OptimizationError("Базисні клітинки не утворюють зв'язного дерева.")
        return u, v

    @staticmethod
    def estimates(problem, plan, u, v):
        """Генератор оцінок Δ_ij для небазисних клітинок: (i, j, Δ)."""
        for i, j, c in problem.cells():
            if (i, j) not in plan:
                yield i, j, c - u[i] - v[j]

    def _entering_cell(self, problem, plan, u, v):
        best = None
        for i, j, delta in self.estimates(problem, plan, u, v):
            if delta < -EPS and (best is None or delta < best[0]):
                best = (delta, (i, j))
        return None if best is None else best[1]

    @staticmethod
    def find_cycle(plan: Dict[Cell, float], entering: Cell) -> List[Cell]:
        """Шукає цикл: вводимо клітинку + шлях по базису від стовпця до рядка."""
        i0, j0 = entering
        by_row: Dict[int, List[int]] = {}
        by_col: Dict[int, List[int]] = {}
        for (i, j) in plan:
            by_row.setdefault(i, []).append(j)
            by_col.setdefault(j, []).append(i)
        start, goal = ("c", j0), ("r", i0)
        # Пошук у ширину по базису: шлях від стовпця j0 до рядка i0
        parent = {start: None}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node == goal:
                break
            kind, k = node
            neighbours = ([(("c", j), (k, j)) for j in by_row.get(k, [])] if kind == "r"
                          else [(("r", i), (i, k)) for i in by_col.get(k, [])])
            for nxt, edge in neighbours:
                if nxt not in parent:
                    parent[nxt] = (node, edge)
                    queue.append(nxt)
        if goal not in parent:
            raise OptimizationError("Не вдалося побудувати цикл перерозподілу.")
        path: List[Cell] = []
        node = goal
        while parent[node] is not None:
            node, edge = parent[node]
            path.append(edge)
        path.reverse()  # від стовпця j0 до рядка i0
        return [entering] + path

    def _shift(self, plan: Dict[Cell, float], entering: Cell) -> None:
        cycle = self.find_cycle(plan, entering)
        plus = cycle[0::2]   # знаки: +, −, +, − ...
        minus = cycle[1::2]
        # θ — найменше перевезення серед клітинок зі знаком «−»
        theta = min(plan[c] for c in minus)
        leaving = next(c for c in minus if plan[c] == theta)
        plan[entering] = 0
        for c in plus:
            plan[c] += theta
        for c in minus:
            plan[c] -= theta
            if is_zero(plan[c]):
                plan[c] = 0
        # Клітинка, що обнулилась, виходить із базису
        del plan[leaving]
