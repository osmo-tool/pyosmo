from pyosmo.algorithm.base import OsmoAlgorithm


class RandomAlgorithm(OsmoAlgorithm):
    def choose(self, history, choices):
        return self.random.choice(choices)
