"""
Same example as in README.md but in executable format
"""
from pyosmo.algorithm.random import RandomAlgorithm
from pyosmo.end_conditions.length import Length
from pyosmo.osmo import Osmo


class ExampleModel:

    def __init__(self):
        print('starting')
        self._counter = 0

    def before_test(self):
        self._counter = 0

    def guard_decrease(self):
        return self._counter > 1

    def step_decrease(self):
        self._counter -= 1
        print("- {}".format(self._counter))

    def guard_increase(self):
        return self._counter < 100

    def step_increase(self):
        self._counter += 1
        print("+ {}".format(self._counter))


osmo = Osmo()
osmo.add_model(ExampleModel())
osmo.set_algorithm(RandomAlgorithm())
osmo.set_test_end_condition(Length(100))
osmo.set_suite_end_condition(Length(100))
osmo.generate(seed=333)
