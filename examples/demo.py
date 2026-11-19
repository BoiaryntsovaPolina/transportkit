"""Демонстрація роботи бібліотеки transportkit.

Запуск (після встановлення пакета):  python examples/demo.py
"""

from pathlib import Path

from transportkit import (Stopwatch, TransportError, compare_methods, load_problem,
                          save_solution, solve)

problem = load_problem(Path(__file__).with_name("problem.json"))
print(problem, "\n")

print("Порівняння методів побудови опорного плану:")
with Stopwatch() as watch:
    for solution in compare_methods(problem):
        print(f"  {solution.method:<36} Z = {solution.total_cost}")
print(f"  (усі методи за {watch.elapsed * 1000:.2f} мс)\n")

try:
    best = solve(problem, method="vogel", optimize=True)
except TransportError as error:
    print("Помилка:", error)
else:
    print(best)
    print("\nНенульові перевезення:")
    for i, j, quantity in best:
        print(f"  {best.problem.row_label(i)} -> {best.problem.col_label(j)}: {quantity}")
    save_solution(best, "solution.json")
    print("\nРозв'язок збережено у solution.json")
