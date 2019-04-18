from algorithm.base import osmoAlgorithm


class RandomAlgorithm(osmoAlgorithm):
    def choose(self, history, choices):
        return self.random.choice(choices)
