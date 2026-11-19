"""transportkit — невелика бібліотека для розв'язання транспортних задач.

Містить методи побудови початкового опорного плану (кутові, мінімальної вартості,
подвійної переваги, Фогеля) та метод потенціалів для знаходження оптимального плану.

>>> from transportkit import TransportProblem, solve
>>> p = TransportProblem([[2, 3], [4, 1]], supply=[20, 30], demand=[25, 25])
>>> solve(p, "vogel").total_cost
85
"""

from .exceptions import (InvalidFileFormatError, InvalidProblemError, OptimizationError,
                         TransportError, UnknownMethodError)
from .initial import (DoublePreference, InitialMethod, MinCostByColumn, MinCostByRow,
                      MinCostByTable, NorthEastCorner, NorthWestCorner, SouthEastCorner,
                      SouthWestCorner, Vogel)
from .io import load_problem, save_problem, save_solution
from .optimization import PotentialsMethod
from .problem import TransportProblem
from .solution import TransportSolution
from .solver import METHODS, available_methods, compare_methods, solve
from .utils import Stopwatch

__version__ = "1.0.0"

__all__ = [
    "TransportProblem", "TransportSolution", "solve", "compare_methods", "available_methods",
    "METHODS", "PotentialsMethod", "InitialMethod",
    "NorthWestCorner", "NorthEastCorner", "SouthWestCorner", "SouthEastCorner",
    "MinCostByRow", "MinCostByColumn", "MinCostByTable", "DoublePreference", "Vogel",
    "load_problem", "save_problem", "save_solution", "Stopwatch",
    "TransportError", "InvalidProblemError", "UnknownMethodError", "OptimizationError",
    "InvalidFileFormatError", "__version__",
]
