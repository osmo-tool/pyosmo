from pyosmo.algorithm.base import OsmoAlgorithm


class RandomAlgorithm(OsmoAlgorithm):
    """ Fully random algorithm """

    def choose(self, history, choices):
        return self.random.choice(choices)
