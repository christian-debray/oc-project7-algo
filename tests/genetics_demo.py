import time
import random
from typing import Sequence
from genetics import KnapSackSelection, CombinationChromosome
import csv
import argparse
from pathlib import Path
import os


def distribution(pop: Sequence[CombinationChromosome]) -> dict[float, float]:
    pop_size = len(pop)
    dist = dict()
    for chrom in pop:
        dist[chrom.fitness] = dist.get(chrom.fitness, 0) + 1 / pop_size
    return dist


def avg_fitness(pop: Sequence[CombinationChromosome]) -> float:
    total_fitness = 0
    for x in pop:
        total_fitness += x.fitness
    return total_fitness/len(pop)


def parse_args():
    p = argparse.ArgumentParser("genetics_demo")
    p.add_argument("csv_file", nargs="?", default="")
    p.add_argument("--export-data")
    p.add_argument("--import-data")
    args = p.parse_args()
    csv_file = None
    export_data = None
    import_data = None
    if args.csv_file:
        csv_file = make_file(args.csv_file)
    if args.import_data:
        import_data = make_file(args.import_data)
    elif args.export_data:
        export_data = make_file(args.export_data)
    return (csv_file, import_data, export_data)


def make_file(file_n: str) -> Path:
    f = Path(Path(os.getcwd()), file_n).absolute()
    if not f.exists():
        if not f.parent.exists():
            f.parent.mkdir(mode=0o777, parents=True)
        f.touch(mode=0o666)
    return f


def print_distribution(selection: KnapSackSelection):
    dist = distribution(selection.population)
    total = 0
    med = False
    dist_str = []
    for f, d in dist.items():
        st = f"{round(f, 2)}: {round(100*d, 1)}%"
        total += d
        if not med and total >= 0.5:
            st = f"[{st}]"
            med = True
        dist_str.append(st)

    print("distribution: ", " | ".join(dist_str))


(csv_file, import_data, export_data) = parse_args()
if import_data:
    print(f"Importing data from {import_data}...")
    items = []
    with open(import_data, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            items.append((int(row[0]), int(row[1])))
    chromo_size = len(items)
else:
    chromo_size = 1000
    items = [
        (random.randrange(1, 10), random.randrange(20, 30)) for _ in range(chromo_size)
    ]

if export_data:
    print(f"Exporting data to {export_data}...")
    with open(export_data, "w", encoding="utf8") as f:
        writer = csv.writer(f)
        for row in items:
            writer.writerow(row)

pop_size = 500
start = time.perf_counter()
selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=80)
selection.mutation_proba = 0.05
selection.mating_pop = 0.5
selection.elite = 0.1
selection.crossover_operator = "single_point_crossover"
selection.initialize_population()
print(
    f"\nGen {selection.generation}: {selection.best_individual().fitness} {round(100*selection.best_so_far_prevalence(), 1)}%"
)
print_distribution(selection)
MAX_GENERATION = 50
# generation, best fitness, prevalence, execution time
scores = [
    (
        selection.generation,
        selection.best_individual().fitness,
        selection.best_so_far_prevalence(),
        avg_fitness(selection.population),
        0
    )
]
stop = 10
while selection.generation < MAX_GENERATION and stop > 0:
    cycle_start = time.perf_counter()
    best = selection.select()
    cycle_time = round(time.perf_counter() - cycle_start, 6)
    avg = avg_fitness(selection.population)
    scores.append(
        (
            selection.generation,
            best.fitness,
            selection.best_so_far_prevalence(),
            avg,
            cycle_time,
        )
    )
    stable = ""
    if selection.stabilized():
        stable = ""
        stop -= 1
        stable = " (STABLE) "
    print(
        f"\nGen {selection.generation}{stable}: {best.fitness} {round(100*selection.best_so_far_prevalence(), 1)}%  ~ {avg} | {cycle_time}s"
    )
    print_distribution(selection)
end = time.perf_counter() - start
print(f"Done in {round(end, 3)}s ({selection.generation} generations)")

if csv_file:
    print(f"Export to {csv_file}")
    with open(csv_file, "w", encoding="utf8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            ["generation", "best fitness", "prevalence", "avg fitness", "execution time"]
        )
        for r in scores:
            csv_writer.writerow(r)
