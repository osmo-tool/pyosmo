from typing import List

from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.history.history import OsmoHistory
from pyosmo.model import TestStep


class WeightedAlgorithm(OsmoAlgorithm):
    """ Weighted random algorithm """

    def choose(self, history: OsmoHistory, choices: List[TestStep]) -> TestStep:
        return self.random.choices(choices, weights=[c.weight for c in choices])[0]


class WeightedBalancingAlgorithm(OsmoAlgorithm):
    """ Weighted algorithm which balances based on history """

    def choose(self, history: OsmoHistory, choices: List[TestStep]) -> TestStep:
        weights = [c.weight for c in choices]
        normalized_weights = [float(i) / max(weights) for i in weights]

        history_counts = [history.get_step_count(choice) for choice in choices]
        history_weights = [(sum(history_counts) - h) for h in history_counts]
        if max(history_weights) == 0:
            history_normalized_weights = [0] * len(choices)
        else:
            history_normalized_weights = [float(i) / max(history_weights) for i in history_weights]

        total_weights = [nw + history_normalized_weights[i] for i, nw in enumerate(normalized_weights)]

        return self.random.choices(choices, weights=total_weights)[0]
