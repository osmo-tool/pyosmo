# pylint: disable=bare-except
from pyosmo.end_conditions.length import Length
from pyosmo.error_strategy.always_ignore import AlwaysIgnore
from pyosmo.error_strategy.always_raise import AlwaysRaise
from pyosmo.osmo import Osmo


class JustFailModel:
    def __init__(self, exception):
        self.exception = exception

    def step_just_fail(self):
        raise self.exception


def test_always_raise():
    osmo = Osmo(JustFailModel(AssertionError('Failing test_stop_on_failure')))
    osmo.set_test_end_condition(Length(100))
    osmo.set_suite_end_condition(Length(100))
    osmo.test_failure_strategy = AlwaysRaise()
    osmo.test_suite_failure_strategy = AlwaysRaise()
    try:
        osmo.generate()
    except:
        pass
    assert osmo.history.total_amount_of_steps == 1


def test_always_ignore():
    osmo = Osmo(JustFailModel(AssertionError('Failing test_always_ignore')))
    osmo.set_test_end_condition(Length(100))
    osmo.set_suite_end_condition(Length(10))
    osmo.test_failure_strategy = AlwaysIgnore()
    osmo.test_suite_failure_strategy = AlwaysIgnore()
    try:
        osmo.generate()
    except:
        pass
    assert osmo.history.total_amount_of_steps == 10 * 100
