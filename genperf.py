"""Evaluate performance of GA
"""
from genetics import CombinationSelection
import time
import random


def select_execution_time(pop_size=100, chromo_size=1000):
    """Evaluates execution time of a full selection cycle."""
    ellapsed: list[float] = list()
    tries = 100
    for _ in range(tries):
        selection = CombinationSelection(
            population_size=pop_size, chromosome_size=chromo_size
        )
        selection.initialize_population()
        start = time.perf_counter()
        selection.select()
        ellapsed.append(time.perf_counter() - start)
    max_ellapsed = max(ellapsed)
    return max_ellapsed


def time_scale():
    """Time scale = avg time to sort 1000 elements in a list.
    """
    s = time.perf_counter()
    for _ in range(1000):
        rand_arr = [random.randrange(1, pow(2, 20)) for _ in range(1000)]
        rand_arr.sort()
    time_scale = (time.perf_counter() - s) / 1000
    return time_scale


pop_size = 100

print("Evaluate time scale...")
acceptable = 20 * time_scale()
for chromo_size in (100, 500, 1000):
    print(f"With chromo_size = {chromo_size}")
    print("   Evaluate selection execution time...")
    cycle_exec_time = select_execution_time(pop_size=pop_size, chromo_size=chromo_size)
    success = "SUCCESS" if (cycle_exec_time <= acceptable + .0001) else "FAILURE"
    print(f"   => {success}: avg exec time = {round(cycle_exec_time, 3)}s | acceptable = {round(acceptable, 3)}s")
