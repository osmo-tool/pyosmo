from typing import List

from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.history.history import OsmoHistory
from pyosmo.model import TestStep


class WeightedAlgorithm(OsmoAlgorithm):
    """ Weighted random algorithm """

    def choose(self, history: OsmoHistory, choices: List[TestStep]) -> TestStep:
        return self.random.choices(choices, weights=[c.weight for c in choices])[0]
