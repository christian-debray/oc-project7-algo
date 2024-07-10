from dataclasses import dataclass


@dataclass
class Action:
    name: str
    value: float
    efficiency: float

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.name.upper()} {self.value}$ {round(self.efficiency*100)}%"

    def __hash__(self) -> int:
        return self.__str__().__hash__()


def actions_stats(*act: Action) -> tuple[float, float]:
    """Returns stats of a set of actions:
    total value and profit
    """
    t_value = 0.0
    t_profit = 0.0
    for a in act:
        t_value += a.value
        t_profit += a.value * a.efficiency
    return (t_value, t_profit)


def actions_constraint(max_value: float = None, min_profit: float = None):
    """Test a set of actions and return True if condition is verified.
    """
    def predicate(*action_set: Action):
        satisfied: bool = True
        stats = actions_stats(*action_set)
        if max_value:
            satisfied = satisfied and stats[0] <= max_value
        if min_profit:
            satisfied = satisfied and stats[1] >= min_profit
        return satisfied
    return predicate


@dataclass
class Share:
    name: str
    value: float
    efficiency: float
    hash_val: int = None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.name.upper()} {self.value}$ {round(self.efficiency*100)}%"

    def __hash__(self) -> int:
        if self.hash_val:
            return self.hash_val
        else:
            return self.__str__().__hash__()


class StockPortfolio:
    def __init__(self, *shares: Share):
        self.stock: frozenset[Share] = frozenset(shares)
        self._value: float = 0.0
        self._profit: float = 0.0
        for s in shares:
            self._value += s.value
            self._profit += s.value * s.efficiency

    def in_stock(self, s: Share):
        return s in self.stock

    def total_value(self):
        return self._value

    def profit(self):
        return round(self._profit, 2)

    def add(self, s: Share) -> 'StockPortfolio':
        if (s not in self.stock):
            new_stock = StockPortfolio()
            new_stock.stock = self.stock | frozenset([s])
            new_stock._value = self._value + s.value
            new_stock._profit = self._profit + s.efficiency * s.value
            return new_stock
        else:
            return None

    def remove(self, s: Share) -> 'StockPortfolio':
        if s in self.stock:
            new_stock = StockPortfolio()
            new_stock.stock = self.stock - frozenset([s])
            new_stock._value = self._value - s.value
            new_stock._profit = self._profit - s.value * s.efficiency
            return new_stock
        else:
            return None

    def __str__(self) -> str:
        return f"StockPortfolio {len(self.stock)} shares, value={self.total_value()}, profit={self.profit()}"
