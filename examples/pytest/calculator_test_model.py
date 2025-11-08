import pyosmo


@pyosmo.weight(10)  # Set default weight for this class steps
class CalculatorTestModel(pyosmo.OsmoModel):
    """This is a simple test model for demonstration purposes"""

    def __init__(self):
        print('starting')
        self.expected_number = 0

    def before_test(self):
        """This is executer always before new test case starts"""
        print('New test starts')
        self.expected_number = 0

    def guard_minus(self):
        """It is always possible to reduce the number in this model,
        then returning True always"""
        return True

    def step_minus(self):
        """The action what happens in case of minus button is pressed"""
        numb = int(self.osmo_random.random() * 10)
        print(f'{self.expected_number} - {numb} = {self.expected_number - numb}')
        self.expected_number -= numb

    @pyosmo.weight(2)
    def step_plus(self):
        """Number increase happens two times more often and then weight is 2
        step_plus do not have guard, which means that it is always possible step"""
        numb = int(self.osmo_random.random() * 10)
        print(f'{self.expected_number} + {numb} = {self.expected_number + numb}')
        self.expected_number += numb

    def step_multiple(self):
        """Multiplying action"""
        numb = int(self.osmo_random.random() * 10)
        print(f'{self.expected_number} * {numb} = {self.expected_number * numb}')
        self.expected_number *= numb

    def step_division(self):
        """Division action"""
        numb = int(self.osmo_random.random() * 10)
        # Zero is not possible
        if numb == 0:
            numb = 2
        print(f'{self.expected_number} / {numb} = {self.expected_number // numb}')
        self.expected_number //= numb

    @pyosmo.weight(0.1)
    def step_clear(self):
        """Clearing the state happens very rarely"""
        self.expected_number = 0
        print(0)

    def after(self):
        """This is executed after each test case"""
        display = self.expected_number
        print(f'Assert: {display = }')


if __name__ == '__main__':
    # Initialize Osmo with model
    osmo = pyosmo.Osmo(CalculatorTestModel())
    osmo.test_end_condition = pyosmo.end_conditions.Length(100)
    osmo.algorithm = pyosmo.algorithm.WeightedAlgorithm()

    # Generate tests
    osmo.generate()
    osmo.history.print_summary()
