# pylint: disable=no-self-use,bare-except

from pyosmo.end_conditions.length import Length
from pyosmo.osmo import Osmo


class TestModel:
    def __init__(self):
        self.index = 0

    def step_one(self):
        self.index += 1
        if self.index == 5:
            raise Exception("Should happen!")


def test_exception_raise_effects():
    model = TestModel()
    osmo = Osmo(model)
    osmo.set_test_end_condition(Length(8))
    osmo.set_suite_end_condition(Length(1))
    try:
        osmo.generate()
    except:
        # Osmo is raisin error so need to catch it here
        pass
    assert model.index == 5
