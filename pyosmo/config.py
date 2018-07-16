from pyosmo.algorithm.random import RandomAlgorithm


class OsmoConfig(object):
    def __init__(self):
        self._stop_on_failure = True
        self._algorithm = RandomAlgorithm()

    @property
    def stop_on_failure(self):
        return self._stop_on_failure

    @stop_on_failure.setter
    def stop_on_failure(self, value):
        self._stop_on_failure = value

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
