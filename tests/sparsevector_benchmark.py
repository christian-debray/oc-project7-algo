from helpers.sparsevector import SparseVector
import time
import random


def iteration_benchmark(cycles, size, density: float):
    """iterating over non-zero values should be more efficient with SparseVector"""
    dense = [(1 if random.random() < density else 0) for _ in range(size)]
    dense_start = time.perf_counter()
    for _ in range(cycles):
        a = 0
        for v in dense:
            a += v * 10
    dense_ellapsed = time.perf_counter() - dense_start
    dense_avg_time = round(dense_ellapsed / cycles, 6)
    vec = SparseVector(dense)
    vec_start = time.perf_counter()
    for _ in range(cycles):
        a = 0
        for i, v in vec.non_zeros():
            a += v * 10
    vec_ellapsed = time.perf_counter() - vec_start
    vec_avg_time = round(vec_ellapsed / cycles, 6)

    return (vec_avg_time, dense_avg_time, vec.count_non_zeros())


def concatenation_benchmark(cycles, size, density: float):
    """Concatenating sparse vectors should be as efficient as concatenating lists"""
    dense1 = [(1 if random.random() < density else 0) for _ in range(size//2)]
    dense2 = [(1 if random.random() < density else 0) for _ in range(size//2)]
    dense_start = time.perf_counter()
    for _ in range(cycles):
        d = dense1 + dense2
    dense_ellapsed = round((time.perf_counter() - dense_start) / cycles, 6)
    vec1 = SparseVector(dense1)
    vec2 = SparseVector(dense2)
    vec_start = time.perf_counter()
    for _ in range(cycles):
        v = vec1 + vec2
    vec_ellapsed = round((time.perf_counter() - vec_start) / cycles, 6)
    return (vec_ellapsed, dense_ellapsed, v.count_non_zeros())


def slicing_benchmark(cycles, size, density: float):
    """Concatenating sparse vectors should be as efficient as concatenating lists"""
    dense = [(1 if random.random() < density else 0) for _ in range(size)]
    sl_start = random.randint(0, len(dense)//2)
    sl_stop = sl_start + (len(dense)//2 - 1)
    dense_start = time.perf_counter()
    for _ in range(cycles):
        d = dense[sl_start:sl_stop]
    dense_ellapsed = round((time.perf_counter() - dense_start) / cycles, 6)
    vec = SparseVector(dense)
    vec_start = time.perf_counter()
    for _ in range(cycles):
        v = vec[sl_start:sl_stop]
    vec_ellapsed = round((time.perf_counter() - vec_start) / cycles, 6)
    return (vec_ellapsed, dense_ellapsed, v.count_non_zeros())


size = 1000
cycles = 10000
for density in [.01, .1, .2, .5]:
    print(f"testing with density {density}...")
    vec, dense, k = iteration_benchmark(cycles, size, density)
    print(f"   iterate over nonzeros ({density}): {vec}, {k} / {dense}, {size} / {round(100 * vec/dense, 2)}%")
    vec, dense, k = concatenation_benchmark(cycles, size, density)
    print(f"   concatenation ({density}): {vec}, {k} / {dense}, {size} / {round(100 * vec/dense, 2)}%")
    vec, dense, k = slicing_benchmark(cycles, size, density)
    print(f"   slicing ({density}): {vec}, {k} / {dense}, {size} / {round(100 * vec/dense, 2)}%")
