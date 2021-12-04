from pyosmo.algorithm.base import OsmoAlgorithm


class WeightedAlgorithm(OsmoAlgorithm):
    """ Weighted random algorithm """

    def choose(self, history, choices):
        return self.random.choices(choices, weights=[c.weight for c in choices])[0]
