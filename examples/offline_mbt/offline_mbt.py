"""
Simple example model
"""

import pyosmo


class CalculatorModel(pyosmo.OsmoModel):

    def __init__(self, f):
        self.expected_result = 0
        self.file = f
        self.max_number = 1000
        self.min_number = -1000
        self.test_number = 0

    def before_suite(self):
        self.file.write('# pylint: disable=too-many-lines\n')
        self.file.write('from examples.offline_mbt.sut_calculator import CalculatorSUT\n')

    def before_test(self):
        self.test_number += 1
        self.file.write(f'\n\ndef test_{self.test_number}_calculator():\n')
        self.file.write('    calculator = CalculatorSUT()\n')
        self.expected_result = 0

    def guard_plus(self):
        return self.expected_result < self.max_number

    def step_plus(self):
        number_to_add = self.osmo_random.randint(0, self.max_number - self.expected_result)
        self.expected_result += number_to_add
        self.file.write(f'    calculator.plus({number_to_add})\n')
        self.file.write(f'    assert calculator.display == {self.expected_result}\n')

    def guard_minus(self):
        return self.expected_result > self.min_number

    def step_increase(self):
        number_to_decrease = self.osmo_random.randint(0, abs(self.min_number - self.expected_result))
        self.expected_result -= number_to_decrease
        self.file.write(f'    calculator.minus({number_to_decrease})\n')
        self.file.write(f'    assert calculator.display == {self.expected_result}\n')


if __name__ == '__main__':
    with open('generated_test.py', 'w', encoding='utf8') as file:
        # Initialize Osmo with model
        osmo = pyosmo.Osmo()
        osmo.add_model(CalculatorModel(file))
        # Generate tests
        osmo.test_end_condition = pyosmo.end_conditions.Length(10)
        osmo.test_suite_end_condition = pyosmo.end_conditions.Length(100)
        osmo.generate()
    print('Tests generated in generated_test.py')
    print('run "pytest generated_test.py" to executing tests')
