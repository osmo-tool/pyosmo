from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.history.history import OsmoHistory
from pyosmo.model import TestStep


class RandomAlgorithm(OsmoAlgorithm):
    """Fully random algorithm"""

    def choose(self, history: OsmoHistory, choices: list[TestStep]) -> TestStep:
        if self.random is None:
            raise RuntimeError('Algorithm not initialized. Call initialize() first.')
        return self.random.choice(choices)
