from pyosmo import Osmo, weight
from pyosmo.algorithm import WeightedAlgorithm
from pyosmo.end_conditions import Length


def test_weighted_algorithm():
    class WeightTestModel:
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

    model = WeightTestModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedAlgorithm()
    osmo.generate()

    step_first_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_first"))
    step_second_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_second"))
    step_third_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_third"))

    assert step_first_count < step_second_count < step_third_count


def test_weighted_algorithm_class_default():
    @weight(10)  # Set default weight for class functions
    class WeightTestModel:
        steps = []

        @weight(5)
        def step_first(self):
            self.steps.append('step_first')

        def step_second(self):
            self.steps.append('step_second')

    model = WeightTestModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedAlgorithm()
    osmo.generate()

    step_first_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_first"))
    step_second_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_second"))

    assert step_first_count < step_second_count
