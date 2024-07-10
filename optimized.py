from action import Share, StockPortfolio, actions_stats
import csv
import time
from pathlib import Path
from collections import deque
import math


DATAFILE = Path(Path(__file__).parent, "data", "actions_data.csv").resolve()


def problem_size(search_space):
    s = 0
    for k in range(len(search_space)):
        s += math.comb(len(search_space), k + 1)
    return s


data: list[Share] = []
hash_pow = 0
hash_all = 0
with open(DATAFILE, "r") as csv_file:
    reader = csv.DictReader(csv_file, delimiter=";", quotechar='"')
    for row in reader:
        hash = pow(2, hash_pow)
        data.append(Share(row["action"], float(row["prix"]), float(row["rendement"]), hash))
        hash_all = hash_all + hash
        hash_pow += 1

MAX_VALUE = 500
search_data = data
best_combination = (0, None, 0, 0)
solutions: list[tuple[list[Share], float, float]] = []
initial_stats = actions_stats(*search_data)
portfolio_queue = deque([(search_data.copy(), initial_stats[0], initial_stats[1], hash_all)])
explored = set()

print("OPTIMIZED ALGO")
print(f"{len(search_data)} elements in search space.")
print("Problem size: ", problem_size(search_data))
print("searching solutions ...")

perf = time.perf_counter()
idx = 0
seed = StockPortfolio()
while seed.total_value() + data[idx].value <= MAX_VALUE:
    seed = seed.add(data[idx])
    idx += 1
best_combination = (seed.profit(), list(iter(seed.stock)), seed.total_value(), 0)

c = 0
while len(portfolio_queue):
    ellapsed = round(time.perf_counter() - perf, 3)
    c += 1
    portfolio, total_value, profit, hash = portfolio_queue.popleft()

    if hash in explored:
        continue
    print(
        f"searching #{len(explored):<9} / {len(solutions):<9} / {best_combination[0]} ({ellapsed}s)\r",
        end="",
    )
    explored.add(hash)
    if (total_value <= MAX_VALUE):
        solutions.append((portfolio, total_value, profit))
        if profit > best_combination[0]:
            best_combination = (profit, portfolio, total_value, hash)
        continue
    if profit < best_combination[0]:
        continue
    for i, s in enumerate(portfolio):
        next_portfolio = portfolio.copy()
        next_portfolio.pop(i)
        next_hash = hash - s.hash_val
        n_profit = profit - s.value * s.efficiency
        n_total_value = total_value - s.value
        if next_hash not in explored and n_profit >= best_combination[0]:
            portfolio_queue.append((next_portfolio, n_total_value, n_profit, next_hash))

ellapsed = round(time.perf_counter() - perf, 3)

if best_combination[1]:
    actions_list = [a for a in best_combination[1]]
    actions_list.sort(key=lambda x: x.value)
    sol_str = "   " + "\n   ".join([str(x) for x in actions_list])
    print("\n\nBest solution:", best_combination[3])
    print(sol_str)
    print(f" value  = {best_combination[2]}\n profit = {round(best_combination[0], 2)}")
else:
    print("No solution found !")

print(f"\nOptimized algo completed in {ellapsed} seconds")
