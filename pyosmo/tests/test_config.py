# pylint: disable=no-self-use

from pyosmo.config import OsmoConfig
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
    osmo.stop_on_fail(False)
    osmo.stop_test_on_exception(False)
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


def test_configs_effects():
    model = TestModel()
    osmo = Osmo(model)
    osmo.steps_in_a_test = 8
    osmo.tests_in_a_suite = 1
    osmo.generate()
    assert model.index == 5
    model.index = 0
    osmo.current_test_number = 0
    osmo.stop_on_fail(False)
    osmo.stop_test_on_exception(False)
    osmo.generate()
    assert model.index == 8
