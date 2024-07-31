from genetics import CombinationChromosome, CombinationSelection
from action import Share, StockPortfolio


class StockPortfolioSelection(CombinationSelection):
    def __init__(self, shares_list: list[Share], population_size: int, max_value: int = 500, cls=None):
        self._genes_class = cls or list
        super().__init__(population_size, len(shares_list))
        self.shares_list: list[Share] = shares_list
        self.max_value = max_value

    def fitness_score(self, chrom: CombinationChromosome) -> float:
        total_value = 0
        objective = 0
        for g_idx in chrom.view_bit_indexes():
            total_value += self.shares_list[g_idx].value
            objective += self.shares_list[g_idx].efficiency * self.shares_list[g_idx].value
        if total_value > self.max_value:
            return -1
        else:
            return round(objective, 3)

    def chromosome2StockPortfolio(self, chrom: CombinationChromosome) -> StockPortfolio:
        shares = list()
        for g_idx, g_val in enumerate(chrom.genome):
            if g_val:
                shares.append(self.shares_list[g_idx])
        return StockPortfolio(*shares)

    def best_solution(self) -> StockPortfolio:
        return self.chromosome2StockPortfolio(self.population[0])
