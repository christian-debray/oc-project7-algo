from typing import TypeVar
import random
import statistics

T = TypeVar("T")


class CombinationChromosome:
    mutation_proba: float = 0.75

    def __init__(self, genome):
        self.fitness = -1
        self.genome = [(1 if int(x) else 0) for x in genome]

    def mate(self, other: "CombinationChromosome") -> "CombinationChromosome":
        """Crossover operator. Also applies muttion operator (see mutation_proba).

        """
        if other.genome == self.genome:
            offspring = CombinationChromosome(self.genome)
        else:
            i1 = random.randrange(1, len(self.genome) // 2)
            i2 = i1 + random.randrange(1, len(self.genome) // 2 - 1)
            offspring_genome = other.genome[:i1] + self.genome[i1:i2] + other.genome[i2:]
            offspring = CombinationChromosome(offspring_genome)
        if random.random() < self.mutation_proba:
            offspring.mutate()
        return offspring

    def crossover(self, other: "CombinationChromosome") -> tuple["CombinationChromosome", "CombinationChromosome"]:
        if other.genome == self.genome:
            offspring = (CombinationChromosome(self.genome), CombinationChromosome(self.genome))
        else:
            i1 = random.randrange(1, len(self.genome) // 2)
            i2 = i1 + random.randrange(1, len(self.genome) // 2 - 1)
            offspring_genome_1 = other.genome[:i1] + self.genome[i1:i2] + other.genome[i2:]
            offspring_genome_2 = self.genome[:i1] + other.genome[i1:i2] + self.genome[i2:]
            offspring = (CombinationChromosome(offspring_genome_1), CombinationChromosome(offspring_genome_2))
        if random.random() < self.mutation_proba:
            offspring[0].mutate()
        if random.random() < self.mutation_proba:
            offspring[1].mutate()
        return offspring

    def mutate(self):
        """swap a random gene"""
        g1_idx = random.randrange(0, len(self.genome))
        self.genome[g1_idx] = 1 - self.genome[g1_idx]
        # g2_idx = random.choice(
        #     [i for i in range(0, g1_idx)]
        #     + [i for i in range(g1_idx + 1, len(self.genome))]
        # )
        # assert g1_idx != g2_idx
        # g1 = self.genome[g1_idx]
        # g2 = self.genome[g2_idx]
        # self.genome[g1_idx] = g2
        # self.genome[g2_idx] = g1

    def key(self):
        return "".join([str(b) for b in self.genome])


class CombinationSelection:
    def __init__(self, population_size: int, chromosome_size: int):
        self.population: list[CombinationChromosome] = list()
        self.distribution: dict[str, int] = {}
        self.population_size = population_size
        self.elite = 0.1
        self.mating_pop = 0.5
        self.chromosome_size = chromosome_size
        self._convergence_stats: list[float] = []

    def initialize_population(self):
        """"""
        while len(self.population) < self.population_size:
            chrom = self.random_individual(self.chromosome_size)
            chrom.fitness = self.fitness_score(chrom)
            self.add_chromosome(chrom)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self._convergence_stats = [self.convergence()]

    def add_chromosome(self, chrom: CombinationChromosome):
        self.population.append(chrom)
        self.distribution[chrom.key()] = self.distribution.get(chrom.key(), 0) + 1

    def random_individual(self, chromosome_size) -> CombinationChromosome:
        """"""
        genome = [random.randint(0, 1) for _ in range(chromosome_size)]
        return CombinationChromosome(genome)

    def fitness_score(self, chrom: CombinationChromosome) -> float:
        """Default implementation: return the number coded by the genome.
        Bigger is better.
        """
        score = 0
        for idx, g in enumerate(chrom.genome):
            score += g * pow(2, idx)
        return score

    def select(self):
        """"""
        s = int(self.population_size * self.elite)
        new_generation = self.population[:s]
        mid = int(self.population_size * self.mating_pop)
        while len(new_generation) < self.population_size:
            parent1 = random.choice(self.population[:mid])
            parent2 = random.choice(self.population[:mid])
            #child = parent1.mate(parent2)
            child1, child2 = parent1.crossover(parent2)
            child1.fitness = self.fitness_score(child1)
            child2.fitness = self.fitness_score(child2)
            #child.fitness = self.fitness_score(child)
            new_generation.append(child1)
            new_generation.append(child2)
        new_generation.sort(key=lambda x: x.fitness, reverse=True)
        self.population = new_generation
        self.distribution = {}
        for chrom in self.population:
            self.distribution[chrom.key()] = self.distribution.get(chrom.key(), 0) + 1
        self._convergence_stats.append(self.convergence())

    def select_parent(
        self, first_parent: CombinationChromosome = None
    ) -> CombinationChromosome:
        """Select parents for crossover operation.
        Several strategies are possible: elitism, roulette wheel, tournament, ...
        """

    def _tournament_selection(self, pop, k):
        """Select the fittest chromosome among k random chromosome found in a population"""

    def convergence(self) -> float:
        return self.distribution[self.population[0].key()] / len(self.population)

    def stabilized(self):
        if len(self._convergence_stats) < 6 or self.convergence() < 0.5:
            return False
        if self.convergence() > 0.9:
            return True
        if self._convergence_stats[len(self._convergence_stats) - 5] < 0.5:
            return
        sample = self._convergence_stats[len(self._convergence_stats) - 5:]
        return statistics.mean(sample) / max(sample) > 0.9


def elite_selection(pop: list[CombinationChromosome], elite: float) -> CombinationChromosome:
    """Select a random chromosome among the n fittest in a population"""
    limit = int(elite*len(pop))
    idx = random.randint(0, limit - 1)
    return pop[idx]


def tournament_selection(
    k, population: list[CombinationChromosome]
) -> CombinationChromosome:
    """Select the fittest chromosome among k elements randomly chosen from a population."""
    best = None
    idx_list = [i for i in range(len(population))]
    for _ in range(k):
        idx = idx_list.pop(random.randrange(0, len(idx_list)))
        if best is None:
            best = population[idx]
        elif best.fitness < population[idx].fitness:
            best = population[idx]
    return best
