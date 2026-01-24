from datetime import datetime, timedelta

import pytest
from hypothesis import given
from hypothesis.strategies import integers

from pyosmo import Osmo
from pyosmo.end_conditions import And, Length, Or, StepCoverage, Time


class TempModel:
    def __init__(self):
        self.counter = 0

    def step_first(self):
        self.counter += 1

    def step_second(self):
        self.counter += 1


@given(steps=integers(1, 100), tests=integers(1, 10))
def test_length_end_condition(steps, tests):
    model = TempModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(tests)
    osmo.test_suite_end_condition = Length(steps)
    osmo.generate()
    assert model.counter == steps * tests


def test_test_time_end_condition():
    time_in_sec = 1
    osmo = Osmo(TempModel())
    osmo.test_end_condition = Time(timedelta(seconds=time_in_sec))
    osmo.test_suite_end_condition = Length(1)
    start_time = datetime.now()
    osmo.generate()
    end_time = datetime.now()
    duration = end_time - start_time
    assert duration < timedelta(seconds=time_in_sec + 0.1)
    assert duration > timedelta(seconds=time_in_sec - 0.1)


def test_test_suite_time_end_condition():
    time_in_sec = 1
    osmo = Osmo(TempModel())
    osmo.test_end_condition = Length(1)
    osmo.test_suite_end_condition = Time(timedelta(seconds=time_in_sec))
    start_time = datetime.now()
    osmo.generate()
    end_time = datetime.now()
    duration = end_time - start_time
    assert duration < timedelta(seconds=time_in_sec + 0.1)
    assert duration > timedelta(seconds=time_in_sec - 0.1)


def test_logical_and():
    model = TempModel()
    osmo = Osmo(model)
    osmo.test_end_condition = And(Length(1), Length(2), Length(3))
    osmo.test_suite_end_condition = And(Length(2), Length(3), Length(4))
    osmo.generate()
    assert model.counter == 3 * 4


def test_logical_or():
    model = TempModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Or(Length(1), Length(2), Length(3))
    osmo.test_suite_end_condition = Or(Length(2), Length(3), Length(4))
    osmo.generate()
    assert model.counter == 2


def test_step_coverage():
    model = TempModel()
    osmo = Osmo(model)
    osmo.test_end_condition = StepCoverage(100)
    osmo.test_suite_end_condition = Length(1)
    osmo.generate()

    step_first = osmo.model.get_step_by_name('step_first')
    step_second = osmo.model.get_step_by_name('step_second')
    assert step_first is not None
    assert step_second is not None

    assert osmo.history.get_step_count(step_first) > 0
    assert osmo.history.get_step_count(step_second) > 0


def test_step_coverage_valid_values():
    """StepCoverage should accept values 1-100 inclusive"""
    StepCoverage(1)
    StepCoverage(50)
    StepCoverage(99)
    StepCoverage(100)


def test_step_coverage_invalid_values():
    """StepCoverage should reject values outside 1-100"""
    with pytest.raises(Exception, match='Coverage is'):
        StepCoverage(0)
    with pytest.raises(Exception, match='Coverage is'):
        StepCoverage(-1)
    with pytest.raises(Exception, match='Coverage is'):
        StepCoverage(101)


def test_step_coverage_mid_range():
    """StepCoverage with 50% should stop when half the steps are covered"""
    model = TempModel()
    osmo = Osmo(model)
    osmo.test_end_condition = StepCoverage(50)
    osmo.test_suite_end_condition = Length(1)
    osmo.generate()
    # With 2 steps and 50% coverage, at least 1 step must have been used
    step_first = osmo.model.get_step_by_name('step_first')
    step_second = osmo.model.get_step_by_name('step_second')
    used_first = osmo.history.get_step_count(step_first) > 0
    used_second = osmo.history.get_step_count(step_second) > 0
    assert used_first or used_second


def test_step_coverage_end_suite_cumulative():
    """StepCoverage as suite end condition should check coverage across ALL test cases"""

    class SingleStepModel:
        """Model where only one step is available at a time, alternating per test"""

        def __init__(self):
            self.test_number = 0

        def before_test(self):
            self.test_number += 1

        def step_first(self):
            pass

        def guard_first(self):
            return self.test_number % 2 == 1

        def step_second(self):
            pass

        def guard_second(self):
            return self.test_number % 2 == 0

    model = SingleStepModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(1)
    osmo.test_suite_end_condition = StepCoverage(100)
    osmo.generate()
    # Suite should stop once both steps have been used across multiple tests
    step_first = osmo.model.get_step_by_name('step_first')
    step_second = osmo.model.get_step_by_name('step_second')
    assert osmo.history.get_step_count(step_first) > 0
    assert osmo.history.get_step_count(step_second) > 0
