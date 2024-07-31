from action import Share, StockPortfolio
import csv
import time
from pathlib import Path
import math
from genetic_solution import StockPortfolioSelection
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("datafile")
parser.add_argument("--pop-size", type=int, nargs="?", default=200)
parser.add_argument("--max-gen", type=int, nargs="?", default=50)
parser.add_argument("--attempts", type=int, nargs="?", default=1)
parser.add_argument("--max-value", type=float, nargs="?", default=500)
args = parser.parse_args()

# DATAFILE = Path(Path(__file__).parent, "data", "actions_data.csv").resolve()
# DATAFILE = Path(Path(__file__).parent, "data", "dataset1_Python+P7.csv").resolve()
DATAFILE = Path(os.getcwd(), args.datafile).resolve()


def problem_size(search_space):
    s = 0
    for k in range(len(search_space)):
        s += math.comb(len(search_space), k + 1)
    return s


data: list[Share] = []
with open(DATAFILE, "r") as csv_file:
    reader = csv.DictReader(csv_file, delimiter=",")
    r_count = 0
    for row in reader:
        r_count += 1
        price = float(row.get("price", 0))
        profit = float(row.get("profit", 0))
        if profit >= 1:
            profit = profit / 100
        if price > 0 and profit > 0:
            data.append(Share(row["name"], price, profit))


print(f"Input dataset loaded: {len(data)}/{r_count} valid rows from {DATAFILE}.")

SERIES = args.attempts
MAX_GEN = args.max_gen
start = time.perf_counter()
MAX_VALUE = args.max_value
POP_SIZE = args.pop_size
local_maxima: list[StockPortfolio] = []
for i in range(SERIES):
    selection = StockPortfolioSelection(data, POP_SIZE, MAX_VALUE)
    selection.initialize_population()
    t = 0
    while t < MAX_GEN and not selection.stabilized():
        t += 1
        selection.select()
        print(
            f"{i} / {t}: {round(100*selection.best_so_far_prevalence())}% / {selection.best_solution().profit()}\r",
            end="",
        )
        if selection.stabilized():
            print("")
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
print(f" value  = {round(best.total_value(), 2)}\n profit = {round(best.profit(), 2)}")

print(f"\nOptimized algo completed in {ellapsed} seconds")
