import time
import random
from typing import Sequence
from genetics import KnapSackSelection, CombinationChromosome


def distribution(pop: Sequence[CombinationChromosome]) -> dict[float, float]:
    pop_size = len(pop)
    dist = dict()
    for chrom in pop:
        dist[chrom.fitness] = dist.get(chrom.fitness, 0) + 1/pop_size
    return dist


pop_size = 200
chromo_size = 100
items = [(random.randrange(1, 10), random.randrange(20, 30)) for _ in range(chromo_size)]

start = time.perf_counter()
selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=80)
selection.mutation_proba = .15
selection.crossover_operator = 'uniform_crossover'
#  selection.crossover_operator = 'single_point_crossover'
selection.mating_pop = .5
selection.initialize_population()
tries = 100
scores = [(0, selection.best_individual().fitness, selection.best_so_far_prevalence(), 0)]
for g in range(tries):
    cycle_start = time.perf_counter()
    best = selection.select()
    cycle_time = round(time.perf_counter() - cycle_start, 6)
    scores.append((g, best.fitness, selection.best_so_far_prevalence(), cycle_time))
    stable = " (STABLE) " if selection.stabilized() else ""
    print(f"\nGen {g}{stable}: {best.fitness} {round(100*selection.best_so_far_prevalence(), 1)}% {cycle_time}s")
    dist = distribution(selection.population)
    total = 0
    med = False
    dist_str = []
    for f, d in dist.items():
        st = f"{round(f, 2)}: {round(100*d, 1)}%"
        total += d
        if not med and total >= .5:
            st = f"[{st}]"
            med = True
        dist_str.append(st)

    print("distribution: ", " | ".join(dist_str))
end = time.perf_counter() - start
print(f"Done in {round(end, 3)}s ({g} generations)")
