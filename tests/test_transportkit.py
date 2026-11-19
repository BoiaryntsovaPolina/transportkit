"""Прості тести бібліотеки transportkit.

Запуск:  python -m unittest discover -s tests -v
"""

import os
import tempfile
import unittest

from transportkit import (InvalidProblemError, TransportProblem, UnknownMethodError,
                          available_methods, load_problem, save_problem, solve)

# Задача, для якої оптимальна вартість відома: Z = 650
PROBLEM = TransportProblem(
    costs=[[2, 3, 4, 2, 4], [8, 4, 1, 4, 1], [9, 7, 3, 7, 2]],
    supply=[60, 80, 100],
    demand=[40, 30, 50, 60, 60],
)


class TestTransportkit(unittest.TestCase):

    def test_closed_problem_is_balanced(self):
        # Сума запасів дорівнює сумі потреб
        self.assertTrue(PROBLEM.is_balanced)

    def test_open_problem_gets_fictitious_consumer(self):
        # Запасів більше, ніж потреб: має з'явитись фіктивний споживач
        problem = TransportProblem([[1, 2], [3, 4]], supply=[30, 30], demand=[20, 20])
        balanced = problem.balanced()
        self.assertTrue(balanced.is_balanced)
        self.assertEqual(balanced.n, 3)

    def test_north_west_and_vogel_costs(self):
        # Вартості початкових планів, перевірені вручну
        self.assertEqual(solve(PROBLEM, "nw", optimize=False).total_cost, 710)
        self.assertEqual(solve(PROBLEM, "vogel", optimize=False).total_cost, 690)

    def test_every_method_builds_valid_plan(self):
        # Кожен із 9 методів має дати допустимий план
        for key in available_methods():
            solution = solve(PROBLEM, key, optimize=False)
            self.assertTrue(solution.is_feasible(), key)

    def test_potentials_give_optimum(self):
        # З будь-якого початкового плану метод потенціалів приходить до Z = 650
        for key in available_methods():
            self.assertEqual(solve(PROBLEM, key).total_cost, 650, key)

    def test_negative_supply_is_rejected(self):
        with self.assertRaises(InvalidProblemError):
            TransportProblem([[1, 2]], supply=[-5], demand=[1, 1])

    def test_unknown_method_is_rejected(self):
        with self.assertRaises(UnknownMethodError):
            solve(PROBLEM, "magic")

    def test_json_save_and_load(self):
        # Записали задачу у файл і прочитали назад — вона не змінилась
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "problem.json")
            save_problem(PROBLEM, path)
            self.assertEqual(load_problem(path), PROBLEM)


if __name__ == "__main__":
    unittest.main()
