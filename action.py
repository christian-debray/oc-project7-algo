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
