# pylint: disable=no-self-use
from random import Random

import pyosmo
from pyosmo import OsmoModel
from pyosmo.algorithm import WeightedAlgorithm
from pyosmo.end_conditions import Length
from pyosmo.osmo import Osmo


class CalculatorTestModel(OsmoModel):

    def __init__(self, random: Random = Random()):
        print('starting')
        self.expected_number = 0
        self.random = random

    def before_test(self):
        print('New test starts')
        self.expected_number = 0

    def guard_minus(self):
        return True

    def step_minus(self):
        numb = int(self.random.random() * 10)
        print(f"{self.expected_number} - {numb} = {self.expected_number - numb}")
        self.expected_number -= numb

    @pyosmo.weight(2)  # This happens two times more often than normally
    def step_plus(self):
        numb = int(self.random.random() * 10)
        print(f"{self.expected_number} + {numb} = {self.expected_number + numb}")
        self.expected_number += numb

    def step_multiple(self):
        numb = int(self.random.random() * 10)
        print(f"{self.expected_number} * {numb} = {self.expected_number * numb}")
        self.expected_number *= numb

    def step_division(self):
        numb = int(self.random.random() * 10)
        # Zero is not possible
        if numb == 0:
            numb = 2
        print(f"{self.expected_number} / {numb} = {self.expected_number / numb}")
        self.expected_number /= numb

    @pyosmo.weight(0.1)  # this happens 10 times less ofthen usually
    def step_clear(self):
        self.expected_number = 0
        print(0)

    def after(self):
        display = self.expected_number
        print(f'Assert: {display = }')


if __name__ == '__main__':
    # Initialize Osmo with model
    osmo = Osmo(CalculatorTestModel())
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedAlgorithm()

    # Generate tests
    osmo.generate()
    osmo.history.print_summary()
