# transportkit

Невелика бібліотека на Python для розв'язання **транспортних задач** (Дослідження операцій).
Містить усі класичні методи побудови початкового опорного плану та метод потенціалів
для знаходження оптимального плану. Не має зовнішніх залежностей.

## Можливості

| Група | Методи (ключ) |
|---|---|
| Кутові | північно-західний `nw`, північно-східний `ne`, південно-західний `sw`, південно-східний `se` |
| Мінімальної вартості | за рядком `min_row`, за стовпцем `min_col`, за таблицею `min_table` |
| Інші | подвійної переваги `double`, Фогеля `vogel` |
| Оптимізація | метод потенціалів (`PotentialsMethod`) |

Додатково: автоматичне балансування відкритих моделей (фіктивний постачальник/споживач),
обробка вироджених планів, збереження/завантаження задач і розв'язків у JSON.

## Встановлення

З готового wheel-файлу (розділ *Releases*):

```bash
pip install transportkit-1.0.0-py3-none-any.whl
```

Або безпосередньо з GitHub:

```bash
pip install git+https://github.com/BoiaryntsovaPolina/transportkit.git
```

## Швидкий старт

```python
from transportkit import TransportProblem, solve, compare_methods

problem = TransportProblem(
    costs=[[2, 3, 4, 2, 4],
           [8, 4, 1, 4, 1],
           [9, 7, 3, 7, 2]],
    supply=[60, 80, 100],
    demand=[40, 30, 50, 60, 60],
)

solution = solve(problem, method="vogel")   # опорний план + метод потенціалів
print(solution)                             # таблиця перевезень і Z
print(solution.total_cost)                  # 650

for s in compare_methods(problem):          # порівняння всіх методів
    print(s.method, s.total_cost)
```

Тільки опорний план, без оптимізації: `solve(problem, "nw", optimize=False)`.

Робота з файлами:

```python
from transportkit import load_problem, save_solution

problem = load_problem("examples/problem.json")
save_solution(solve(problem), "solution.json")
```

## Структура проєкту

```
transportkit/
├── pyproject.toml
├── src/transportkit/
│   ├── problem.py          # TransportProblem — умова задачі
│   ├── solution.py         # TransportSolution — план перевезень
│   ├── initial/            # методи опорного плану (ієрархія класів)
│   │   ├── base.py         #   абстрактний InitialMethod, Allocator
│   │   ├── corner.py       #   чотири кутові методи
│   │   ├── min_cost.py     #   мінімальна вартість: рядок / стовпець / таблиця
│   │   ├── double_preference.py
│   │   └── vogel.py
│   ├── optimization.py     # метод потенціалів
│   ├── solver.py           # solve(), compare_methods(), реєстр методів
│   ├── io.py               # JSON
│   ├── utils.py            # декоратори, контекстний менеджер Stopwatch
│   └── exceptions.py       # власні винятки
├── tests/                  # unittest
└── examples/               # demo.py, problem.json
```

## Тести та збірка

```bash
python -m unittest discover -s tests -v     # запуск тестів
python -m build                             # збірка wheel у каталог dist/
```

