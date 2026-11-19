"""Клас TransportProblem — умова транспортної задачі."""

from __future__ import annotations

import math
from numbers import Real
from typing import Iterator, List, Optional, Tuple

from .exceptions import InvalidProblemError
from .utils import EPS, fmt_number, render_table


class TransportProblem:
    """Транспортна задача: m постачальників, n споживачів, матриця вартостей.

    Дані зберігаються у вигляді кортежів (інкапсуляція): ззовні їх можна
    лише читати через властивості, тому умову не можна випадково змінити.

    >>> p = TransportProblem([[2, 3], [4, 1]], supply=[20, 30], demand=[25, 25])
    >>> p.is_balanced
    True
    >>> p.cost(1, 1)
    1
    """

    def __init__(self, costs, supply, demand, *, name: str = "Транспортна задача") -> None:
        # Дані зберігаємо кортежами: їх не можна випадково змінити ззовні
        self._costs: Tuple[Tuple[Real, ...], ...] = tuple(tuple(row) for row in costs)
        self._supply: Tuple[Real, ...] = tuple(supply)
        self._demand: Tuple[Real, ...] = tuple(demand)
        self._name = name
        self._fictitious_row: Optional[int] = None
        self._fictitious_col: Optional[int] = None
        self._validate()

    # ---------------------------------------------------------------- перевірка
    def _validate(self) -> None:
        # Перевіряємо розмірність, типи та знаки вхідних даних
        if not self._costs or not self._costs[0]:
            raise InvalidProblemError("Матриця вартостей не може бути порожньою.")
        n = len(self._costs[0])
        if any(len(row) != n for row in self._costs):
            raise InvalidProblemError("Усі рядки матриці вартостей мають бути однакової довжини.")
        if len(self._supply) != len(self._costs):
            raise InvalidProblemError(
                f"Кількість запасів ({len(self._supply)}) не збігається "
                f"з кількістю рядків матриці ({len(self._costs)}).")
        if len(self._demand) != n:
            raise InvalidProblemError(
                f"Кількість потреб ({len(self._demand)}) не збігається "
                f"з кількістю стовпців матриці ({n}).")

        for row in self._costs:
            for value in row:
                self._check_number(value, "вартість")
        for value in self._supply:
            self._check_number(value, "запас")
            if value < 0:
                raise InvalidProblemError("Запаси не можуть бути від'ємними.")
        for value in self._demand:
            self._check_number(value, "потреба")
            if value < 0:
                raise InvalidProblemError("Потреби не можуть бути від'ємними.")
        if sum(self._supply) <= 0:
            raise InvalidProblemError("Сумарний запас має бути додатним.")

    @staticmethod
    def _check_number(value, what: str) -> None:
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise InvalidProblemError(f"Некоректне значення ({what}): {value!r}. Очікується скінченне число.")

    # ---------------------------------------------------------------- властивості
    @property
    def costs(self) -> Tuple[Tuple[Real, ...], ...]:
        return self._costs

    @property
    def supply(self) -> Tuple[Real, ...]:
        return self._supply

    @property
    def demand(self) -> Tuple[Real, ...]:
        return self._demand

    @property
    def name(self) -> str:
        return self._name

    @property
    def m(self) -> int:
        """Кількість постачальників (рядків)."""
        return len(self._costs)

    @property
    def n(self) -> int:
        """Кількість споживачів (стовпців)."""
        return len(self._costs[0])

    @property
    def total_supply(self):
        return sum(self._supply)

    @property
    def total_demand(self):
        return sum(self._demand)

    @property
    def is_balanced(self) -> bool:
        """Закрита модель: сума запасів дорівнює сумі потреб."""
        return math.isclose(self.total_supply, self.total_demand, abs_tol=EPS)

    @property
    def fictitious_row(self) -> Optional[int]:
        """Індекс фіктивного постачальника (якщо задачу було збалансовано)."""
        return self._fictitious_row

    @property
    def fictitious_col(self) -> Optional[int]:
        """Індекс фіктивного споживача (якщо задачу було збалансовано)."""
        return self._fictitious_col

    # ---------------------------------------------------------------- методи
    def cost(self, i: int, j: int):
        return self._costs[i][j]

    def row_label(self, i: int) -> str:
        return "A*" if i == self._fictitious_row else f"A{i + 1}"

    def col_label(self, j: int) -> str:
        return "B*" if j == self._fictitious_col else f"B{j + 1}"

    def cells(self) -> Iterator[Tuple[int, int, Real]]:
        """Генератор усіх клітинок: (рядок, стовпець, вартість)."""
        for i, row in enumerate(self._costs):
            for j, value in enumerate(row):
                yield i, j, value

    def balanced(self) -> "TransportProblem":
        """Повертає закриту модель; за потреби додає фіктивного постачальника/споживача.

        Вартості перевезень до/від фіктивного пункту дорівнюють нулю.
        Якщо задача вже збалансована, повертається вона сама.
        """
        if self.is_balanced:
            return self
        # Різниця запасів і потреб показує, що саме додати
        diff = self.total_supply - self.total_demand
        if diff > 0:  # запасів більше — потрібен фіктивний споживач
            costs = [row + (0,) for row in self._costs]
            result = TransportProblem(costs, self._supply, self._demand + (diff,), name=self._name)
            result._fictitious_col = self.n
        else:  # потреб більше — потрібен фіктивний постачальник
            costs = list(self._costs) + [(0,) * self.n]
            result = TransportProblem(costs, self._supply + (-diff,), self._demand, name=self._name)
            result._fictitious_row = self.m
        return result

    # ---------------------------------------------------------------- серіалізація
    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "costs": [list(row) for row in self._costs],
            "supply": list(self._supply),
            "demand": list(self._demand),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TransportProblem":
        return cls(data["costs"], data["supply"], data["demand"],
                   name=data.get("name", "Транспортна задача"))

    # ---------------------------------------------------------------- спеціальні методи
    def __len__(self) -> int:
        return self.m * self.n

    def __iter__(self) -> Iterator[Tuple[int, int, Real]]:
        return self.cells()

    def __getitem__(self, position: Tuple[int, int]):
        i, j = position
        return self._costs[i][j]

    def __eq__(self, other) -> bool:
        if not isinstance(other, TransportProblem):
            return NotImplemented
        return (self._costs, self._supply, self._demand) == (other._costs, other._supply, other._demand)

    def __hash__(self) -> int:
        return hash((self._costs, self._supply, self._demand))

    def __repr__(self) -> str:
        return (f"TransportProblem({self.m}x{self.n}, supply={list(self._supply)}, "
                f"demand={list(self._demand)})")

    def __str__(self) -> str:
        header = [""] + [self.col_label(j) for j in range(self.n)] + ["Запаси"]
        rows: List[list] = []
        for i, row in enumerate(self._costs):
            rows.append([self.row_label(i)] + [fmt_number(c) for c in row] + [fmt_number(self._supply[i])])
        rows.append(["Потреби"] + [fmt_number(d) for d in self._demand] + [fmt_number(self.total_demand)])
        status = "закрита" if self.is_balanced else "відкрита"
        return f"{self._name} ({status} модель)\n" + render_table(header, rows)
