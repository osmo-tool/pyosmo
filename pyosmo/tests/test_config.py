# pylint: disable=no-self-use,bare-except,try-except-raise

from pyosmo import Osmo
from pyosmo.algorithm import RandomAlgorithm
from pyosmo.end_conditions import Length


class TempException(Exception):
    pass


class OneStepModel:
    def __init__(self):
        self.index = 0

    def step_one(self):
        self.index += 1
        if self.index == 5:
            raise TempException("Should happen!")


def test_exception_raise_effects():
    model = OneStepModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(8)
    osmo.test_suite_end_condition = Length(1)
    try:
        osmo.generate()
    except TempException:
        # Osmo is raisin test exception so need to catch it here
        pass
    assert model.index == 5


def test_wrong_config_objects():
    osmo = Osmo(OneStepModel())
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
