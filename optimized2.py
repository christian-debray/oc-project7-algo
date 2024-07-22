from action import Share, StockPortfolio
import csv
import time
from pathlib import Path
import math
from genetic_solution import StockPortfolioSelection


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

start = time.perf_counter()
MAX_VALUE = 500
local_maxima: list[StockPortfolio] = []
for i in range(10):
    selection = StockPortfolioSelection(data, 200, MAX_VALUE)
    selection.initialize_population()
    t = 0
    for _ in range(100):
        t += 1
        selection.select()
        print(f"{i} / {t}: {round(100*selection.convergence())}% / {selection.best_solution().profit()}\r", end="\n")
        if selection.stabilized():
            break
    ellapsed = round(time.perf_counter() - start, 3)
    local_maxima.append(selection.best_solution())
local_maxima.sort(key=lambda x: x.profit())

best = local_maxima[-1]
best_stock = [s for s in best.stock]
best_stock.sort(key=lambda x: x.value)
sol_str = "   " + "\n   ".join([str(x) for x in best_stock])
print("\n\nBest solution:")
print(sol_str)
print(f" value  = {best.total_value()}\n profit = {round(best.profit(), 2)}")

print(f"\nOptimized algo completed in {ellapsed} seconds")
