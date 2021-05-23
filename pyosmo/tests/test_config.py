# pylint: disable=no-self-use,bare-except,try-except-raise

from pyosmo.algorithm.random import RandomAlgorithm
from pyosmo.end_conditions.length import Length
from pyosmo.osmo import Osmo


class TestException(Exception):
    pass


class TestModel:
    def __init__(self):
        self.index = 0

    def step_one(self):
        self.index += 1
        if self.index == 5:
            raise TestException("Should happen!")


def test_exception_raise_effects():
    model = TestModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(8)
    osmo.test_suite_end_condition = Length(1)
    try:
        osmo.generate()
    except TestException:
        # Osmo is raisin test exception so need to catch it here
        pass
    assert model.index == 5


def test_wrong_config_objects():
    osmo = Osmo(TestModel())
    try:
        osmo.test_end_condition = RandomAlgorithm()
    except AttributeError:
        pass
    except:
        raise

    try:
        osmo.algorithm = Length(1)
    except AttributeError:
        pass
    except:
        raise
