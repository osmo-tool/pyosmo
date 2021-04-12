# pylint: disable=no-self-use

from pyosmo.config import OsmoConfig
from pyosmo.end_conditions.length import Length
from pyosmo.osmo import Osmo


class TestModel(object):
    def __init__(self):
        self.index = 0

    def step_one(self):
        self.index += 1
        if self.index == 5:
            raise Exception("Should happen!")


def test_set_configs():
    model = TestModel()
    osmo = Osmo(model)
    assert osmo.config.stop_test_on_exception is True
    assert osmo.config.stop_on_fail is True
    osmo.stop_on_fail = False
    osmo.stop_test_on_exception = False
    assert osmo.config.stop_test_on_exception is False
    assert osmo.config.stop_on_fail is False


def test_config_object():
    cfg = OsmoConfig()
    assert cfg.stop_test_on_exception
    assert cfg.stop_on_fail
    cfg.stop_on_fail = False
    cfg.stop_test_on_exception = False
    assert cfg.stop_test_on_exception is False
    assert cfg.stop_on_fail is False


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


def test_exception_catch_effects():
    model = TestModel()
    osmo = Osmo(model)
    osmo.set_test_end_condition(Length(8))
    osmo.set_suite_end_condition(Length(1))
    model.index = 0
    osmo.stop_test_on_exception = False
    osmo.generate()
    assert model.index == 8
