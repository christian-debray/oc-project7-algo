"""Greedy solution of the 0/1 knapsack problem"""
from action import Share, StockPortfolio
import csv
import time
from pathlib import Path
import argparse
import os


def greedy_knapsack(items: list[Share], max: float):
    sol = StockPortfolio()
    items.sort(key=lambda x: x.value, reverse=True)
    i = 0
    while sol.total_value() + items[i].value <= max:
        sol = sol.add(items[i])
        i += 1
    return sol


parser = argparse.ArgumentParser()
parser.add_argument("datafile")
args = parser.parse_args()

DATAFILE = Path(os.getcwd(), args.datafile).resolve()


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

start = time.perf_counter()
best = greedy_knapsack(data, 500)
ellapsed = time.perf_counter() - start
best_stock = [s for s in best.stock]
best_stock.sort(key=lambda x: x.value)
sol_str = "   " + "\n   ".join([str(x) for x in best_stock])
print("\n\nBest solution:")
print(sol_str)
print(f" value  = {best.total_value()}\n profit = {round(best.profit(), 2)}")

print(f"\nGreedy algo completed in {round(ellapsed, 5)} seconds")