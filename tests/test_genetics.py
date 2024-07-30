import unittest
from genetics import CombinationChromosome, KnapSackSelection
import random


class TestCombinationChromosome(unittest.TestCase):
    """Test methods of the CombinationChromosome class"""

    def test_init_key(self):
        """Construct a combination chromosome from a list of booleans"""
        genome = [0, 1, 0, 0, 1, 0]
        chrom = CombinationChromosome(genome)
        self.assertEqual(chrom.__str__(), "010010")

    def test_mutate(self):
        """Chromosome always mutates by swapping a random gene"""
        genome = [1, 0, 0, 0, 0]
        chrom1 = CombinationChromosome(genome)
        chrom2 = CombinationChromosome(genome)
        mutation_count = 0
        tries = 1000
        for _ in range(tries):
            chrom2 = CombinationChromosome(genome)
            chrom2.mutate()
            if chrom1.key() != chrom2.key():
                mutation_count += 1
            self.assertNotEqual(chrom1.key(), chrom2.key())
        self.assertEqual(
            mutation_count / tries, 1.0
        )

    def test_single_point_crossover(self):
        """Single point crossover combines all genes of both parents in two child chromosome."""
        chrom1 = CombinationChromosome([1, 1, 0, 0, 0])
        chrom2 = CombinationChromosome([0, 0, 0, 1, 1])
        child1, child2 = chrom1.single_point_crossover(chrom2)
        for _ in range(1000):
            # crossover uses a random factor...
            for i in range(len(chrom1.genome)):
                self.assertEqual(chrom1.genome[i] or chrom2.genome[i], child1.genome[i] or child2.genome[i])

    def test_double_point_crossover(self):
        """Double point crossover combines all genes of both parents in two child chromosome."""
        chrom1 = CombinationChromosome([1, 1, 0, 0, 0])
        chrom2 = CombinationChromosome([0, 0, 0, 1, 1])
        child1, child2 = chrom1.two_points_crossover(chrom2)
        for _ in range(1000):
            # crossover uses a random factor...
            for i in range(len(chrom1.genome)):
                self.assertEqual(chrom1.genome[i] or chrom2.genome[i], child1.genome[i] or child2.genome[i])

    def test_uniform_crossover(self):
        """Uniform crossover combines all genes of both parents in two child chromosome."""
        chrom1 = CombinationChromosome([1, 1, 0, 0, 0])
        chrom2 = CombinationChromosome([0, 0, 0, 1, 1])
        child1, child2 = chrom1.uniform_crossover(chrom2)
        for _ in range(1000):
            # crossover uses a random factor...
            for i in range(len(chrom1.genome)):
                self.assertEqual(chrom1.genome[i] or chrom2.genome[i], child1.genome[i] or child2.genome[i])


class TestKnapSackSelection(unittest.TestCase):
    """Test methods of ths CombinationSelection class"""

    def test_knapsack_fitness(self):
        pop_size = 200
        items = [(1, 10), (2, 15), (3, 5), (4, 32), (5, 23), (8, 42)]
        max_weight = 12
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=max_weight)
        chrom1 = CombinationChromosome([1, 0, 0, 0, 0, 0])
        self.assertEqual(selection.fitness_score(chrom1), 10)
        chrom2 = CombinationChromosome([1, 1, 1, 1, 1, 1])
        self.assertEqual(selection.fitness_score(chrom2), -11)
        chrom2 = CombinationChromosome([0, 1, 0, 1, 1, 0])
        self.assertEqual(selection.fitness_score(chrom2), 70)

    def test_guess_density(self):
        """Test guessing of acceptable density of 1s in random chromosomes"""
        pop_size = 200
        chromo_size = 100
        max_weight = 30
        items = [(1, random.randrange(10, 30)) for _ in range(chromo_size)]
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=max_weight)
        density = selection.guess_acceptable_density()
        self.assertAlmostEqual(density, max_weight/chromo_size, delta=.1)

    def test_initialize_population(self):
        """Test CombinationSelection constructor and initial population"""
        pop_size = 200
        chromo_size = 200
        items = [(random.randrange(1, 10), random.randrange(20, 30)) for _ in range(chromo_size)]
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=30)
        selection.initialize_population()
        self.assertEqual(len(selection.population), pop_size)
        for i in range(pop_size - 1):
            self.assertGreaterEqual(
                selection.population[i].fitness, selection.population[i + 1].fitness
            )

    def test_initial_convergence(self):
        """Initial convergence should be lower than 20% for longer chromosomes."""
        pop_size = 200
        chromo_size = 1000
        items = [(random.randrange(1, 10), random.randrange(20, 30)) for _ in range(chromo_size)]
        tries = 100
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=30)
        selection._density = selection.guess_acceptable_density()
        for _ in range(tries):
            selection.initialize_population(auto_density=False)
            initial_convergence = selection.best_so_far_prevalence()
            fail_msg = "initial_convergence ({}) is not less than .2. Top fittness = {}, density = {}"
            self.assertLess(
                initial_convergence,
                0.2,
                fail_msg.format(initial_convergence, selection.best_individual().fitness, selection._density))

    def test_select_top_fitess(self):
        """Fitness of top chromosome should increase after each selection cycle"""
        pop_size = 200
        chromo_size = 1000
        items = [(random.randrange(1, 10), random.randrange(20, 30)) for _ in range(chromo_size)]
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=30)
        selection.initialize_population()
        tries = 50
        fitness_scores = [selection.best_individual().fitness]
        for _ in range(tries):
            fitness_scores.append(selection.select().fitness)
            self.assertGreaterEqual(fitness_scores[-1], fitness_scores[-2])

    def test_stabilized(self):
        """Test stabilized() method with deterministic population"""
        pop_size = 100
        chromo_size = 10
        max_weight = 30
        items = [(i + 1, (i + 1) * 10) for i in range(chromo_size)]
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=max_weight)
        self.assertFalse(selection.stabilized())
        ideal_chromo = [0, 0, 1, 0, 0, 0, 0, 0, 0, 1]
        selection.population = []
        selection.mutation_proba = 0
        for _ in range(int(pop_size*.9)):
            x = CombinationChromosome(ideal_chromo)
            x.fitness = selection.fitness_score(x)
            selection.add_chromosome(x)
        while len(selection.population) < pop_size:
            x = selection.random_individual(chromosome_size=chromo_size)
            x.fitness = selection.fitness_score(x)
            selection.add_chromosome(x)
        self.assertGreaterEqual(selection.best_so_far_prevalence(), .9)
        for _ in range(20):
            selection.select()
        self.assertGreaterEqual(selection.best_so_far_prevalence(), .9)
        self.assertTrue(selection.stabilized())

    def test_convergence(self):
        """Algo should converge, but at least after 10 generations"""
        pop_size = 200
        chromo_size = 100
        items = [(random.randrange(1, 10), random.randrange(20, 30)) for _ in range(chromo_size)]
        selection = KnapSackSelection(population_size=pop_size, items=items, max_weight=30)
        selection.mutation_proba = .15
        selection.elite = 1/pop_size
        selection.mating_pop = .5
        selection.initialize_population()
        max_generation = 1000
        while selection.generation < max_generation and not selection.stabilized():
            selection.select()
        self.assertTrue(selection.stabilized())
        self.assertLess(selection.generation, max_generation)
        self.assertGreaterEqual(selection.generation, 10)
