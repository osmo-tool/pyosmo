import random

from pyosmo.end_conditions.length import Length
from pyosmo.osmo import Osmo


class Calculator:
    """
    Calculator "implementation" which will be tested
    """

    def __init__(self):
        self.result_number = 0

    def add(self, num):
        self.result_number += num

    def minus(self, num):
        # Flaky bug here
        if random.randint(1, 1000) > 995:
            pass
        else:
            self.result_number -= num

    def result(self) -> int:
        return self.result_number


class PositiveCalculator:
    """
    This test model test only positive numbers
    """

    # Reference number which will be compared to the system under testing
    expected_count = 0
    # Connection to the system under testing, just instance in this case
    calculator = Calculator()

    def __init__(self):
        pass

    @staticmethod
    def before_suite():
        """This is executed at the begin of the test suite"""
        print('START')

    def before_test(self):
        """This is executed before each test case"""
        print('Test starts')
        # Initializing variables
        self.expected_count = 0
        self.calculator = Calculator()

    @staticmethod
    def guard_add():
        """It is always able to add when testing positive numbers
        This guard can be deleted because this is default guard when guard is missing"""
        return True

    def step_add(self):
        """Add a number"""
        add_num = random.randint(1, 1000)
        print(f'{self.expected_count} + {add_num} = {self.expected_count + add_num}')
        # Add number to the system under testing
        self.calculator.add(add_num)
        # update reference variable
        self.expected_count += add_num

    def guard_minus(self):
        """This is allowed only when count is positive"""
        return self.expected_count > 0

    def step_minus(self):
        """Minus random number"""
        minus_num = random.randint(1, self.expected_count)
        print(f'{self.expected_count} - {minus_num} = {self.expected_count - minus_num}')
        # Minus number from system under testing
        self.calculator.minus(minus_num)
        # update reference variable
        self.expected_count -= minus_num

    def after(self):
        """This happend after each test step"""
        print(f'assert {self.calculator.result()} == {self.expected_count}')
        assert self.calculator.result() == self.expected_count

    def after_test(self):
        """This is executed after each test"""
        print(f'Test ends, final number: {self.expected_count}\n')

    @staticmethod
    def after_suite():
        print('END')


if __name__ == '__main__':
    # Add model to the osmo
    osmo = Osmo(PositiveCalculator())
    # Setup test amount per suite
    osmo.test_end_condition = Length(10)
    # Set steps amount in test case
    # Try to add bigger number of test steps to see when rare bug is cached
    osmo.test_end_condition = Length(1)
    # Run model
    osmo.generate()
