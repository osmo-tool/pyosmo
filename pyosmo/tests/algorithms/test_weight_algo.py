from pyosmo import Osmo, weight
from pyosmo.algorithm import WeightedAlgorithm, WeightedBalancingAlgorithm
from pyosmo.end_conditions import Length


class WeightTestModel1:
    steps = []

    @weight(1)
    def step_first(self):
        self.steps.append('step_first')

    @weight(2)
    def step_second(self):
        self.steps.append('step_second')

    @staticmethod
    def weight_third():
        # More dynamic way to define weight
        return 3

    def step_third(self):
        self.steps.append('step_third')


def test_weighted_algorithm():
    model = WeightTestModel1()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedAlgorithm()
    osmo.generate()

    step_first_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_first"))
    step_second_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_second"))
    step_third_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_third"))

    assert step_first_count < step_second_count < step_third_count


@weight(10)  # Set default weight for class functions
class WeightTestModel2:
    steps = []

    @weight(5)
    def step_first(self):
        self.steps.append('step_first')

    def step_second(self):
        self.steps.append('step_second')


def test_weighted_algorithm_class_default():
    model = WeightTestModel2()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedAlgorithm()
    osmo.generate()

    step_first_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_first"))
    step_second_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_second"))

    assert step_first_count < step_second_count


def test_weighted_balancing_algorithm_class_default():
    model = WeightTestModel2()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedBalancingAlgorithm()
    osmo.generate()

    step_first_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_first"))
    step_second_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_second"))

    assert step_first_count < step_second_count
