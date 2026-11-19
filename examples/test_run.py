from transportkit import TransportProblem, solve, compare_methods, __version__

print("transportkit", __version__)
problem = TransportProblem(
    costs=[[2, 3, 4, 2, 4], [8, 4, 1, 4, 1], [9, 7, 3, 7, 2]],
    supply=[60, 80, 100],
    demand=[40, 30, 50, 60, 60],
)
for s in compare_methods(problem):
    print(f"{s.method:<34} Z = {s.total_cost}")
print()
print(solve(problem, "vogel"))
