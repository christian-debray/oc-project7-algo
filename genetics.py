from typing import TypeVar, Sequence
import random
import statistics
from abc import abstractmethod
import math

T = TypeVar("T")


class CombinationChromosome:
    mutation_proba: float = 0.75
    crossover_operator = "single_point_crossover"

    def __init__(self, genome: Sequence):
        self.fitness = -1
        self.genome = genome[:]

    def crossover(
        self, other: "CombinationChromosome", operator="single_point_crossover"
    ) -> tuple["CombinationChromosome", "CombinationChromosome"]:
        """Crossover operator. Produces 2 new Chromosomes, which may mutate.

        By default, performs a single point crossover.
        An alternative crossover operator can be set with the second optional parameter."""
        crossover_method = getattr(self, operator)
        return crossover_method(other)

    def single_point_crossover(
        self, other: "CombinationChromosome"
    ) -> tuple["CombinationChromosome", "CombinationChromosome"]:
        """Crossover implementation with a single crossover point, producing 2 descendants."""
        i = random.randrange(0, len(self.genome))
        offspring_genome_1 = self.genome[:i] + other.genome[i:]
        offspring_genome_2 = other.genome[:i] + self.genome[i:]
        return (
            CombinationChromosome(offspring_genome_1),
            CombinationChromosome(offspring_genome_2),
        )

    def two_points_crossover(
        self, other: "CombinationChromosome"
    ) -> tuple["CombinationChromosome", "CombinationChromosome"]:
        """Implementation of a two points crossover operator, producing two descendants."""
        i1 = random.randrange(1, len(self.genome) // 2)
        i2 = random.randrange(len(self.genome) // 2, len(self.genome) - 1)
        offspring_genome_1 = other.genome[:i1] + self.genome[i1:i2] + other.genome[i2:]
        offspring_genome_2 = self.genome[:i1] + other.genome[i1:i2] + self.genome[i2:]
        return (
            CombinationChromosome(offspring_genome_1),
            CombinationChromosome(offspring_genome_2),
        )

    def uniform_crossover(
        self, other: "CombinationChromosome"
    ) -> tuple["CombinationChromosome", "CombinationChromosome"]:
        """Implementation of a uniform crossover, producing two descendants"""
        offspring_genome_1 = self.genome[:]
        offspring_genome_2 = other.genome[:]
        for i in range(len(self.genome)):
            if random.random() < 0.5:
                offspring_genome_1[i] = self.genome[i]
                offspring_genome_2[i] = other.genome[i]
            else:
                offspring_genome_1[i] = self.genome[i]
                offspring_genome_2[i] = other.genome[i]
        return (CombinationChromosome(offspring_genome_1), CombinationChromosome(offspring_genome_2))

    def mutate(self):
        """Swap a random gene."""
        g1_idx = random.randrange(0, len(self.genome))
        self.genome[g1_idx] = 1 - self.genome[g1_idx]

    def view_bit_indexes(self):
        """Return indices of non-zero bits."""
        return [i for i, v in enumerate(self.genome) if v != 0]

    def key(self):
        """Concatenation of non-zero indices."""
        return "".join([str(b) for b in self.view_bit_indexes()])

    def __str__(self):
        """Complete bit string."""
        return "".join([str(b) for b in self.genome])


class CombinationSelection:
    def __init__(self, population_size: int, chromosome_size: int):
        self.population: list[CombinationChromosome] = list()
        self.population_size = population_size
        self.elite = 0.1
        self.mating_pop = 0.5
        self.chromosome_size = chromosome_size
        self._convergence_stats: list[tuple[float, float]] = []
        self._density = 0.1
        self.mutation_proba = 0.15
        self.crossover_operator = 'single_point_crossover'
        self.generation = 0
        self._total_fitness_by_gen: dict[int, float] = dict()

    def initialize_population(self, auto_density: bool = True):
        """intitalize population with random individuals"""
        if (auto_density):
            self._density = self.guess_acceptable_density()
        while len(self.population) < self.population_size:
            chrom = self.random_individual(self.chromosome_size, self._density)
            chrom.fitness = self.fitness_score(chrom)
            self.add_chromosome(chrom)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self._convergence_stats = [(self.best_individual().fitness, self.best_so_far_prevalence())]
        self.generation = 0
        self.total_fitness()

    def guess_acceptable_density(self):
        """Try to guess acceptable density of 1 bits for random individuals.
        """
        full = CombinationChromosome([1 for _ in range(self.chromosome_size)])
        if self.fitness_score(full) > 0:
            return .5
        # Discard density values producing too many unrealistic solutions.
        # We assume that higher density values are more likely to produce unrealistic solutons.
        # density ranges from 0 to .5, we'll search the optimal density by dichotomy.
        min_d = 0
        max_d = .5
        test_d = max_d / 2
        while (max_d - min_d) >= .01:
            below_zero = 0
            for _ in range(10):
                chrom = self.random_individual(self.chromosome_size, test_d)
                # Unrealistic solutions have a fitness score below zero:
                if self.fitness_score(chrom) <= 0:
                    below_zero += 1
            if below_zero >= 5:
                # Discard densities producing too many unrealistic solutions:
                max_d = test_d
            else:
                min_d = test_d
            test_d = min_d + (max_d - min_d)/2
        return test_d

    def add_chromosome(self, chrom: CombinationChromosome):
        self.population.append(chrom)

    def random_individual(self, chromosome_size, density: float = .5) -> CombinationChromosome:
        """random individual. Number of bits equal to 1 is controlled by the density parameter"""
        genes = [
            (1 if random.random() < density else 0)
            for _ in range(chromosome_size)
        ]
        return CombinationChromosome(genes)

    @abstractmethod
    def fitness_score(self, chrom: CombinationChromosome) -> float:
        """Calcualting a fitness score is propblem-dependent.

        Value of the fitness score should increase with the quality of the solution.
        Values of 0 or less should be kept for non-acceptable solutions.
        """
        pass

    def select(self) -> CombinationChromosome:
        """Perform a single selection cycle, with an eltistic approach.
        Returns the best individual found in population.
        """
        s = int(self.population_size * self.elite)
        new_generation = self.population[:s]
        if self.generation < 10:
            probas = self._make_roulette_probas()
        while len(new_generation) < self.population_size:
            if self.generation < 10:
                parent2 = self.roulette_wheel_selection(probas)
                parent1 = self.roulette_wheel_selection(probas)
            else:
                parent1, parent2 = self.tournament_selection(k=10)
            child1, child2 = parent1.crossover(parent2, operator=self.crossover_operator)
            if random.random() < self.mutation_proba:
                child1.mutate()
            if random.random() < self.mutation_proba:
                child2.mutate()
            child1.fitness = self.fitness_score(child1)
            child2.fitness = self.fitness_score(child2)
            new_generation.append(child1)
            new_generation.append(child2)
        new_generation.sort(key=lambda x: x.fitness, reverse=True)
        self.population = new_generation
        self._convergence_stats.append((self.best_individual().fitness, self.best_so_far_prevalence()))
        self.total_fitness()
        self.generation += 1
        return self.best_individual()

    def best_individual(self) -> CombinationChromosome:
        return self.population[0]

    def tournament_selection(
        self, k: int
    ) -> tuple[CombinationChromosome, CombinationChromosome]:
        """Select the 2 fittest chromosomes among k random chromosomes found in a population."""
        if self.mating_pop < 1:
            mid = int(self.population_size * self.mating_pop)
            population = self.population[:mid]
        else:
            population = self.population
        pop_indices = [i for i, _ in enumerate(population)]
        random.shuffle(pop_indices)
        p1 = pop_indices[:k]
        p1.sort(key=lambda x: population[x].fitness, reverse=True)
        parent1 = population[p1[0]]
        p2 = pop_indices[:k]
        p2.sort(key=lambda x: population[x].fitness, reverse=True)
        parent2 = population[p2[0]]
        return (parent1, parent2)

    def total_fitness(self):
        self.generation
        if self.generation in self._total_fitness_by_gen:
            return self._total_fitness_by_gen[self.generation]
        total = 0.0
        for x in self.population:
            total += x.fitness if x.fitness > 0 else math.exp(x.fitness)
        self._total_fitness_by_gen[self.generation] = total
        return total

    def roulette_wheel_selection(self, probas: list[tuple[float, CombinationChromosome]] = None):
        if not probas:
            probas = self._make_roulette_probas()
        dice = random.random()
        low = 0
        high = len(probas)
        while high - low > 1:
            t = low + (high - low)//2
            if probas[t][0] > dice:
                high = t
            elif probas[t][0] < dice:
                low = t
            else:
                break
        return probas[t][1]

    def _make_roulette_probas(self):
        probas = []
        cumul = 0.0
        for i, x in enumerate(self.population):
            cumul += x.fitness/self.total_fitness()
            probas.append((cumul, x, i))
        return probas

    def best_so_far_prevalence(self) -> float:
        """Calculates proportion of individuals in population with top fitness score."""
        top_fitness = self.population[0].fitness
        i = 0
        while i < len(self.population) and self.population[i].fitness >= top_fitness:
            i += 1
        return i / len(self.population)

    def stabilized(self):
        """Returns True if the population has stabilized in some way, and reached a plateau:

        - Best so far individual hasn't change since several generations
        - Proportion of best chromosome in the population reached 90% or reached a plateau
        """
        sample_size = 10
        if len(self._convergence_stats) < sample_size:
            return False
        fitness_sample = [x[0] for x in self._convergence_stats[len(self._convergence_stats) - sample_size:]]
        if fitness_sample.count(self.best_individual().fitness) == sample_size:
            if self._convergence_stats[-1][1] >= 0.9:
                return True
            prevalence_sample = [x[1] for x in self._convergence_stats[len(self._convergence_stats) - sample_size:]]
            stability = statistics.mean(prevalence_sample) / max(prevalence_sample)
            return stability >= .9
        else:
            return False


class KnapSackSelection(CombinationSelection):
    """A solution of the 0-1 Knapsack problem using GA.
    """
    def __init__(self, population_size: int, items: list[tuple[int, int]], max_weight: int):
        """Items: tuples (weight, value)"""
        super().__init__(population_size, len(items))
        self.items = items
        self.max_weight = max_weight

    def fitness_score(self, chrom: CombinationChromosome) -> float:
        """Fitness score of a knapsack.

        Fitness evaluates to values below zero when the total weight of items exceeds  max_weight.
        Otherwise, fitness evaluates to the sum of the items values."""
        weight = 0
        value = 0
        for idx in chrom.view_bit_indexes():
            weight += self.items[idx][0]
            value += self.items[idx][1]
        if weight > self.max_weight:
            return self.max_weight - weight
        else:
            return value
