from action import Share, StockPortfolio
import csv
import time
from pathlib import Path
import math
from genetic_solution import StockPortfolioSelection
from helpers.sparsevector import SparseVector
import random

DATAFILE = Path(Path(__file__).parent.parent, "data", "actions_data.csv").resolve()
DATAFILE = Path(Path(__file__).parent.parent, "data", "dataset2_Python+P7.csv").resolve()


data: list[Share] = []
hash_pow = 0
hash_all = 0
with open(DATAFILE, "r") as csv_file:
    reader = csv.DictReader(csv_file, delimiter=",")
    for row in reader:
        price = float(row.get("price", 0))
        profit = float(row.get("profit", 0))
        if profit >= 1:
            profit = profit / 100
        if price > 0 and profit > 0:
            hash = pow(2, hash_pow)
            data.append(Share(row["name"], price, profit, hash))
            hash_all = hash_all + hash
            hash_pow += 1


def benchmark_fitness_score(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, 200, cls=genes_class)
    start = time.perf_counter()
    for _ in range(cycles):
        chrom = selector.random_individual(len(data), 0.01)
        fitness = selector.fitness_score(chrom)
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


def benchmark_crossover(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, 200, cls=genes_class)
    start = time.perf_counter()
    chrom1 = selector.random_individual(len(data), 0.01)
    chrom2 = selector.random_individual(len(data), 0.01)
    for _ in range(cycles):
        chrom1.crossover(chrom2)
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


def benchmark_mutate(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, 200, cls=genes_class)
    start = time.perf_counter()
    chrom1 = selector.random_individual(len(data), 0.01)
    for _ in range(cycles):
        chrom1.mutate()
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


def benchmark_add_chromosome(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, cycles, cls=genes_class)
    chrom = selector.random_individual(selector.chromosome_size)
    chrom.fitness = selector.fitness_score(chrom)
    start = time.perf_counter()
    for _ in range(cycles):
        selector.add_chromosome(chrom)
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


def benchmark_initialization(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, cycles, cls=genes_class)
    start = time.perf_counter()
    for _ in range(cycles):
        selector.initialize_population()
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


def benchmark_sort_population(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, 200, cls=genes_class)
    pop = []
    for _ in range(selector.population_size):
        chrom = selector.random_individual(selector.chromosome_size)
        chrom.fitness = selector.fitness_score(chrom)
        pop.append(chrom)
    start = time.perf_counter()
    for _ in range(cycles):
        pop_copy = pop.copy()
        pop_copy.sort(key=lambda x: x.fitness, reverse=True)
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


def benchmark_selection(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, 200, cls=genes_class)
    ellapsed = 0
    for _ in range(cycles):
        selector.initialize_population()
        start = time.perf_counter()
        selector.select()
        ellapsed += time.perf_counter() - start
    cycle_time = round(ellapsed/cycles, 6)
    return cycle_time


def benchmark_parent_choice(data, genes_class=None, cycles=1000):
    selector = StockPortfolioSelection(data, 200, cls=genes_class)
    selector.initialize_population()
    mid = int(selector.population_size * selector.mating_pop)
    mating_pop = selector.population[:mid]
    start = time.perf_counter()
    for _ in range(cycles):
        _ = selector.tournament_selection(mating_pop, k=len(mating_pop)//5)
    cycle_time = round((time.perf_counter() - start)/cycles, 6)
    return cycle_time


for cls in [list, SparseVector]:
    print(f"class: {cls}")
    print(f"  avg random indiv + fitness = {benchmark_fitness_score(data=data, genes_class=cls)}s (using {cls})")
    print(f"  avg crossover time = {benchmark_crossover(data=data, genes_class=list)}s (using {cls})")
    print(f"  avg mutate time = {benchmark_mutate(data=data, genes_class=list)}s (using {cls})")
    print(f"  avg add chromosome time = {benchmark_add_chromosome(data=data, genes_class=list)}s (using {cls})")
    print(f"  avg initialization time = {benchmark_initialization(data=data, genes_class=list, cycles=10)}s (using {cls})")
    print(f"  avg sort time = {benchmark_sort_population(data=data, genes_class=list)}s (using {cls})")
    print(f"  avg parent choice = {benchmark_parent_choice(data=data, genes_class=list)}s (using {cls})")
    print(f"  avg selection time = {benchmark_selection(data=data, genes_class=list, cycles=100)}s (using {cls})")
