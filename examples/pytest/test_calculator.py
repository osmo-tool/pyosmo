from examples.calculator_test_model import CalculatorTestModel
from pyosmo import Osmo
from pyosmo.algorithm import WeightedAlgorithm, RandomAlgorithm
from pyosmo.end_conditions import Length
from pyosmo.models import RandomDelayModel


def test_smoke():
    # Initialize Osmo with model
    osmo = Osmo(CalculatorTestModel())
    osmo.test_end_condition = Length(10)
    osmo.test_suite_end_condition = Length(1)
    osmo.algorithm = RandomAlgorithm()
    osmo.generate()


def test_regression():
    # Initialize Osmo with model
    osmo = Osmo(CalculatorTestModel())
    osmo.test_end_condition = Length(100)
    osmo.test_suite_end_condition = Length(10)
    osmo.algorithm = WeightedAlgorithm()
    osmo.run()


def test_random_timing():
    # Initialize Osmo with model
    osmo = Osmo(CalculatorTestModel())
    osmo.add_model(RandomDelayModel(1, 2))
    osmo.test_end_condition = Length(10)
    osmo.test_suite_end_condition = Length(1)
    osmo.algorithm = WeightedAlgorithm()
    osmo.run()
