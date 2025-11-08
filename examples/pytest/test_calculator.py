""" This demonstrates how to use model fom pytest side """
import pytest

import pyosmo
from examples.pytest.calculator_test_model import CalculatorTestModel


@pytest.fixture(scope='function')
def osmo() -> pyosmo.Osmo:
    """ You can use common parts in fixtures as normally with pytest """
    return pyosmo.Osmo(CalculatorTestModel())


@pytest.mark.smoke_test
def test_smoke(osmo):
    """ Small test to run quickly and same way """
    osmo.seed = 1234  # Set seed to ensure that it runs same way every time
    osmo.test_end_condition = pyosmo.end_conditions.Length(10)
    osmo.test_suite_end_condition = pyosmo.end_conditions.Length(1)
    osmo.algorithm = pyosmo.algorithm.RandomAlgorithm()
    osmo.run()


@pytest.mark.regression_test
def test_regression(osmo):
    """ Longer test to run in regression sets """
    osmo.test_end_condition = pyosmo.end_conditions.Length(100)
    osmo.test_suite_end_condition = pyosmo.end_conditions.Length(10)
    osmo.algorithm = pyosmo.algorithm.WeightedAlgorithm()
    osmo.run()


@pytest.mark.long_test
def test_random_timing(osmo):
    """ Longer test to test timings """
    osmo.add_model(pyosmo.models.RandomDelayModel(1, 2))
    osmo.test_end_condition = pyosmo.end_conditions.Length(10)
    osmo.test_suite_end_condition = pyosmo.end_conditions.Length(1)
    osmo.algorithm = pyosmo.algorithm.WeightedAlgorithm()
    osmo.run()
