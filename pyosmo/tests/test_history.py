from pyosmo import Osmo
from pyosmo.algorithm import WeightedAlgorithm
from pyosmo.end_conditions import Length


def test_weighted_algorithm():
    class HistoryTest:
        steps = []

        def __init__(self):
            pass

        @staticmethod
        def weight_first():
            return 1

        def step_first(self):
            self.steps.append('step_first')

        @staticmethod
        def weight_second():
            return 2

        def step_second(self):
            self.steps.append('step_second')

        @staticmethod
        def weight_third():
            return 3

        def step_third(self):
            self.steps.append('step_third')

    model = HistoryTest()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_end_condition = Length(100)
    osmo.algorithm = WeightedAlgorithm()
    osmo.generate()

    step_first_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_first"))
    step_second_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_second"))
    step_third_count = osmo.history.get_step_count(osmo.model.get_step_by_name("step_third"))

    assert step_first_count < step_second_count < step_third_count
