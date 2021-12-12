from typing import List

from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.history.history import OsmoHistory
from pyosmo.model import TestStep


class BalancingRandomAlgorithm(OsmoAlgorithm):
    """ This is random algorithm but try to balance coverage.
    In practise rare steps gets more priority when those are available """

    def choose(self, history: OsmoHistory, choices: List[TestStep]) -> TestStep:
        if len(choices) == 1:
            return choices[0]
        history_counts = [history.get_step_count(choice) for choice in choices]
        weights = [(sum(history_counts) - h) for h in history_counts]
        weights = [w - min(weights) + 1 for w in weights]
        ret = self.random.choices(choices, weights=weights)[0]
        return ret


class BalancingAlgorithm(OsmoAlgorithm):
    """ Very simple and eager balancing algorithm """

    def choose(self, history: OsmoHistory, choices: List[TestStep]) -> TestStep:
        history_counts = [history.get_step_count(choice) for choice in choices]
        return choices[history_counts.index(min(history_counts))]
