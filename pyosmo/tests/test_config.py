import contextlib

from pyosmo import Osmo
from pyosmo.algorithm import RandomAlgorithm
from pyosmo.config import ConfigurationError
from pyosmo.end_conditions import Length


class TempError(Exception):
    pass


class OneStepModel:
    def __init__(self):
        self.index = 0

    def step_one(self):
        self.index += 1
        if self.index == 5:
            raise TempError('Should happen!')


def test_exception_raise_effects():
    model = OneStepModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(8)
    osmo.test_suite_end_condition = Length(1)
    with contextlib.suppress(TempError):
        osmo.generate()
    assert model.index == 5


def test_wrong_config_objects():
    osmo = Osmo(OneStepModel())
    try:
        osmo.test_end_condition = RandomAlgorithm()  # type: ignore[assignment]
    except ConfigurationError:
        pass
    except Exception as e:
        raise AssertionError(f'Expected ConfigurationError, got {type(e).__name__}: {e}') from e

    try:
        osmo.algorithm = Length(1)  # type: ignore[assignment]
    except ConfigurationError:
        pass
    except Exception as e:
        raise AssertionError(f'Expected ConfigurationError, got {type(e).__name__}: {e}') from e
