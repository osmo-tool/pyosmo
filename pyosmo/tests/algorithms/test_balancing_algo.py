from pyosmo import Osmo
from pyosmo.algorithm import BalancingAlgorithm, BalancingRandomAlgorithm
from pyosmo.end_conditions import Length


class WeightTestModel:
    steps: list[str] = []

    def step_first(self):
        self.steps.append('step_first')

    # Available every second time, balancing algoritm need to handle this
    def guard_second(self):
        return len(self.steps) % 2 == 0

    def step_second(self):
        self.steps.append('step_second')


def test_balancing_random_algorithm():
    steps_amount = 1000
    model = WeightTestModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(steps_amount)
    osmo.algorithm = BalancingRandomAlgorithm()
    osmo.generate()

    step_first = osmo.model.get_step_by_name('step_first')
    step_second = osmo.model.get_step_by_name('step_second')
    assert step_first is not None
    assert step_second is not None

    step_first_count = osmo.history.get_step_count(step_first)
    step_second_count = osmo.history.get_step_count(step_second)
    difference = step_first_count - step_second_count

    # Difference is less than 20%
    assert difference < steps_amount * 0.2
    # Still need to be some difference
    assert difference > 0


def test_balancing_algorithm():
    steps_amount = 100
    model = WeightTestModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(steps_amount)
    osmo.algorithm = BalancingAlgorithm()
    osmo.generate()

    step_first = osmo.model.get_step_by_name('step_first')
    step_second = osmo.model.get_step_by_name('step_second')
    assert step_first is not None
    assert step_second is not None

    step_first_count = osmo.history.get_step_count(step_first)
    step_second_count = osmo.history.get_step_count(step_second)
    difference = step_first_count - step_second_count

    # Difference need to be very small
    assert difference < 3
