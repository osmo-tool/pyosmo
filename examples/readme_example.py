"""
Simple example model
"""
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


# Initialize Osmo with model
osmo = Osmo(ExampleModel())
# Generate tests
osmo.generate()
