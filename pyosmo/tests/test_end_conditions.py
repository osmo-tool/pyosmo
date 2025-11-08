from datetime import datetime, timedelta

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
