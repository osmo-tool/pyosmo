import time

import pytest

from pyosmo.end_conditions.length import Length
from pyosmo.end_conditions.time import Time
from pyosmo.osmo import Osmo
from random import randint


class TestModel:
    def __init__(self):
        self.counter = 0

    def step_first(self):
        self.counter += 1

    def step_second(self):
        self.counter += 1


@pytest.mark.parametrize("steps", [randint(1, 100) for _ in range(5)])
@pytest.mark.parametrize("tests", [randint(1, 10) for _ in range(3)])
def test_length_end_condition(steps, tests):
    model = TestModel()
    osmo = Osmo(model)
    osmo.set_test_end_condition(Length(tests))
    osmo.set_suite_end_condition(Length(steps))
    osmo.generate()
    assert model.counter == steps * tests


def test_test_time_end_condition():
    time_in_sec = 2
    osmo = Osmo(TestModel())
    osmo.set_test_end_condition(Time(time_in_sec))
    osmo.set_suite_end_condition(Length(1))
    start_time = time.time()
    osmo.generate()
    end_time = time.time()
    duration = end_time - start_time
    assert duration < time_in_sec + 0.1
    assert duration > time_in_sec - 0.1


def test_test_suite_time_end_condition():
    time_in_sec = 2
    osmo = Osmo(TestModel())
    osmo.set_test_end_condition(Length(1))
    osmo.set_suite_end_condition(Time(time_in_sec))
    start_time = time.time()
    osmo.generate()
    end_time = time.time()
    duration = end_time - start_time
    assert duration < time_in_sec + 0.1
    assert duration > time_in_sec - 0.1
