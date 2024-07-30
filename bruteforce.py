from action import Action, actions_stats
from itertools import combinations
import csv
import time
from pathlib import Path
import math
DATAFILE = Path(Path(__file__).parent, "data", "actions_data.csv").resolve()

data: list[Action] = []
with open(DATAFILE, "r") as csv_file:
    reader = csv.DictReader(csv_file, delimiter=",")
    for row in reader:
        data.append(Action(row["name"], float(row["price"]), float(row["profit"])))


def problem_size(search_space):
    s = 0
    for k in range(len(search_space)):
        s += math.comb(len(search_space), k + 1)
    return s


def next_combination(action_list: list[Action]):
    for i in range(1, len(action_list) + 1):
        for comb in combinations(action_list, i):
            yield comb


def comb_str(*act: Action) -> str:
    stats = actions_stats(*act)
    act_str = " + ".join([f"({a})" for a in act])
    return f"{stats[0]} / {stats[1]} : {act_str}"


search_data = data
MAX_VALUE = 500
explored = 0
solutions = []
best_solution = (None, 0, 0)
print("BRUTE FORCE ALGO")
print(f"{len(search_data)} elements in search space.")
print("Problem size: ", problem_size(search_data))
print("searching solutions ...")

perf = time.perf_counter()
for comb in next_combination(search_data):
    explored += 1
    ellapsed = time.perf_counter() - perf
    print(
        f"searching #{explored:<9} / {len(solutions):<9} / {round(best_solution[2], 2):<5} ({round(ellapsed, 3)}s)\r",
        end="",
    )
    stats = actions_stats(*comb)
    if stats[0] <= MAX_VALUE:
        solutions.append(comb)
        if stats[1] > best_solution[2]:
            best_solution = (comb, stats[0], stats[1])


if best_solution[0]:
    actions_list = [a for a in best_solution[0]]
    actions_list.sort(key=lambda x: x.value)
    sol_str = "   " + "\n   ".join([str(x) for x in actions_list])
else:
    sol_str = "None"

print("\n\nBest solution:")
print(sol_str)
print(f" value  = {best_solution[1]}\n profit = {best_solution[2]}")

print(f"\nBrute force algo completed in {round(ellapsed, 3)} seconds")
