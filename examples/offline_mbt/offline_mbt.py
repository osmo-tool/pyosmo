"""
Simple example model
"""
import random

from pyosmo.end_conditions.length import Length
from pyosmo.osmo import Osmo


class CalculatorModel:

    def __init__(self, random, file):
        self.expected_result = 0
        self.random = random
        self.file = file
        self.max_number = 1000
        self.min_number = -1000
        self.test_number = 0

    def before_suite(self):
        self.file.write('from examples.offline_mbt.sut_calculator import CalculatorSUT\n\n')

    def before_test(self):
        self.test_number += 1
        self.file.write('\n\ndef test_{}_calculator():\n'.format(self.test_number))
        self.file.write('    calculator = CalculatorSUT()\n')
        self.expected_result = 0

    def guard_plus(self):
        return self.expected_result < self.max_number

    def step_plus(self):
        number_to_add = random.randint(0, self.max_number - self.expected_result)
        self.expected_result += number_to_add
        self.file.write('    calculator.plus({}) \n'.format(number_to_add))
        self.file.write('    assert calculator.display == {} \n'.format(self.expected_result))

    def guard_minus(self):
        return self.expected_result > self.min_number

    def step_increase(self):
        number_to_decrease = random.randint(0, abs(self.min_number - self.expected_result))
        self.expected_result -= number_to_decrease
        self.file.write('    calculator.minus({}) \n'.format(number_to_decrease))
        self.file.write('    assert calculator.display == {} \n'.format(self.expected_result))


with open('generated_test.py', 'w') as file:
    # Initialize Osmo with model
    osmo = Osmo()
    osmo.add_model(CalculatorModel(osmo.random, file))
    # Generate tests
    osmo.test_end_condition = Length(10)
    osmo.test_suite_end_condition = Length(100)
    osmo.generate()
print('Tests generated in generated_test.py')
print('run "pytest generated_test.py" to executing tests')
