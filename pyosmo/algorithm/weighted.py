from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.history.history import OsmoHistory
from pyosmo.model import TestStep


class WeightedAlgorithm(OsmoAlgorithm):
    """Weighted random algorithm"""

    def choose(self, history: OsmoHistory, choices: list[TestStep]) -> TestStep:
        return self.random.choices(choices, weights=[c.weight for c in choices])[0]


class WeightedBalancingAlgorithm(OsmoAlgorithm):
    """Weighted algorithm which balances based on history"""

    def choose(self, history: OsmoHistory, choices: list[TestStep]) -> TestStep:
        weights = [c.weight for c in choices]
        normalized_weights = [float(i) / max(weights) for i in weights]

        history_counts = [history.get_step_count(choice) for choice in choices]
        if max(history_counts) == 0:
            return self.random.choices(choices, weights=normalized_weights)[0]

        history_normalized_weights = [float(i) / max(history_counts) for i in history_counts]

        total_weights = [
            a - b if a - b != 0 else 0.1 for (a, b) in zip(normalized_weights, history_normalized_weights, strict=True)
        ]

        # Make sure that total weight is more than zero
        if sum(total_weights) < 0:
            temp_add = (abs(sum(total_weights)) + 0.2) / len(total_weights)
            total_weights = [temp_add + x for x in total_weights]

        return self.random.choices(choices, weights=total_weights)[0]
