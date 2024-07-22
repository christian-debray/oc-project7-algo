import unittest
from genetics import CombinationChromosome, CombinationSelection
import math
import time
import random


class TestCombinationChromosome(unittest.TestCase):
    """Test methods of the CombinationChromosome class"""

    def test_init_key(self):
        """Construct a combination chromosome from a list of booleans"""
        genome = [0, 1, 0, 0, 1, 0]
        chrom = CombinationChromosome(genome)
        self.assertEqual(chrom.key(), "010010")

    def test_mutate(self):
        """Chromosome mutates by exchanging two random genes"""
        genome = [1, 0, 0, 0, 0]
        # expected mutation proba for this particular genome:
        # invariant gene exchanges:
        #    comb(2, 4) = 4!/(2!*(2!)) = 24/4 = 6
        # all gene exchanges:
        #    comb(2, 5) = 5!(2*(3!)) = 120/12 = 10
        invariant_mutations = math.comb(len(genome) - 1, 2)
        all_mutations = math.comb(len(genome), 2)
        expected_mutation_proba = 1 - (invariant_mutations / all_mutations)
        chrom1 = CombinationChromosome(genome)
        chrom2 = CombinationChromosome(genome)
        mutation_count = 0
        tries = 1000
        for _ in range(tries):
            chrom2 = CombinationChromosome(genome)
            chrom2.mutate()
            if chrom1.key() != chrom2.key():
                mutation_count += 1
        self.assertAlmostEqual(
            mutation_count / tries, expected_mutation_proba, delta=0.05
        )


class TestCombinationSelection(unittest.TestCase):
    """Test methods of ths CombinationSelection class"""

    def test_initialize_population(self):
        """Test CombinationSelection constructor and initial population"""
        pop_size = 50
        chromo_size = 5
        selection = CombinationSelection(
            population_size=pop_size, chromosome_size=chromo_size
        )
        selection.initialize_population()
        self.assertEqual(len(selection.population), pop_size)
        for i in range(pop_size - 1):
            self.assertGreaterEqual(selection.population[i].fitness, 0)
            self.assertGreaterEqual(selection.population[i + 1].fitness, 0)
            self.assertGreaterEqual(
                selection.population[i].fitness, selection.population[i + 1].fitness
            )

    def test_convergence(self):
        """Initial convergence should be lower than 20% for longer chromosomes."""
        pop_size = 200
        chromo_size = 20
        tries = 1000
        selection = CombinationSelection(
            population_size=pop_size, chromosome_size=chromo_size
        )
        for _ in range(tries):
            selection.initialize_population()
            initial_convergence = selection.convergence()
            self.assertLess(initial_convergence, 0.2)

    def test_select(self):
        """After a few selection cycles, convergence should increase"""
        pop_size = 50
        chromo_size = 10
        selection = CombinationSelection(
            population_size=pop_size, chromosome_size=chromo_size
        )
        selection.initialize_population()
        initial_convergence = selection.convergence()
        tries = 10
        for _ in range(tries):
            selection.select()
        self.assertGreater(selection.convergence(), initial_convergence)

    def test_premature_convergence(self):
        """Population doesn't converge too quickly
        """
        pop_size = 200
        chromo_size = 20
        tries = 100
        cycles = list()
        optimum = CombinationChromosome([1 for _ in range(chromo_size)])
        optimum_reached = 0
        for _ in range(tries):
            selection = CombinationSelection(
                population_size=pop_size, chromosome_size=chromo_size
            )
            optimum.fitness = selection.fitness_score(optimum)
            selection.initialize_population()
            self.assertLessEqual(selection.convergence(), 0.15)
            for i in range(50):
                selection.select()
                if selection.stabilized():
                    break
            cycles.append(i)
            failure_params = f"cycles = {i}, best = {selection.population[0].fitness}/{optimum.fitness}"
            if selection.population[0].fitness != optimum.fitness:
                self.assertAlmostEqual(
                    selection.population[0].fitness / optimum.fitness,
                    1,
                    delta=0.001,
                    msg=f"premature convergence; {failure_params}",
                )
            else:
                optimum_reached += 1
        self.assertGreaterEqual(optimum_reached, .9*tries)

    def test_select_execution_time(self):
        """Selection is fast enough."""
        pop_size = 100
        chromo_size = 1000
        # compare execution time with sorting a big array)
        ellapsed: list[float] = list()
        tries = 100
        acceptable = 20*self._time_scale()
        for _ in range(tries):
            selection = CombinationSelection(
                population_size=pop_size, chromosome_size=chromo_size
            )
            selection.initialize_population()
            start = time.perf_counter()
            selection.select()
            ellapsed.append(time.perf_counter() - start)
        max_ellapsed = max(ellapsed)
        # longest execution time is below acceptable threshold
        self.assertLess(max_ellapsed, acceptable)

    def _time_scale(self):
        s = time.perf_counter()
        for i in range(1000):
            rand_arr = [random.randrange(1, pow(2, 20)) for _ in range(1000)]
            rand_arr.sort()
        time_scale = (time.perf_counter() - s) / 100
        return time_scale


class TestTournamentSelection(unittest.TestCase):
    def test_tournament_selection(self):
        pop: list[CombinationChromosome] = []
        chromo_size = 100
        for i in range(20):
            chromo_val = random.randrange(1, 2**chromo_size)
            chromo_seq = (f"{chromo_val:b}").rjust(chromo_size, '0')
            pop.append(CombinationChromosome(chromo_seq))
        