import time

import pytest

from pyosmo.end_conditions.endless import Endless
from pyosmo.end_conditions.length import Length
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
def test_step_without_guard(steps, tests):
    model = TestModel()
    osmo = Osmo(model)
    osmo.set_suite_end_condition(Length(steps))
    osmo.set_test_end_condition(Length(tests))
    osmo.generate()
    assert model.counter == steps * tests
