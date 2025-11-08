
from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.history.history import OsmoHistory
from pyosmo.model import TestStep


class RandomAlgorithm(OsmoAlgorithm):
    """Fully random algorithm"""

    def choose(self, history: OsmoHistory, choices: list[TestStep]) -> TestStep:
        return self.random.choice(choices)
