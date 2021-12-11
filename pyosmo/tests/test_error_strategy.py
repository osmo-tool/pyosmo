# pylint: disable=bare-except
from pyosmo import Osmo
from pyosmo.end_conditions import Length
from pyosmo.error_strategy import AllowCount, AlwaysIgnore, AlwaysRaise


class JustFailModel:
    def __init__(self, exception):
        self.exception = exception

    def step_just_fail(self):
        raise self.exception


def test_always_raise():
    osmo = Osmo(JustFailModel(AssertionError('Failing test_stop_on_failure')))
    osmo.test_end_condition = Length(100)
    osmo.test_suite_end_condition = Length(100)
    osmo.test_error_strategy = AlwaysRaise()
    osmo.test_suite_error_strategy = AlwaysRaise()
    try:
        osmo.generate()
    except AssertionError:
        pass
    assert osmo.history.total_amount_of_steps == 1


def test_always_ignore():
    osmo = Osmo(JustFailModel(AssertionError('Failing test_always_ignore')))
    osmo.test_end_condition = Length(100)
    osmo.test_suite_end_condition = Length(10)
    osmo.test_error_strategy = AlwaysIgnore()
    osmo.test_suite_error_strategy = AlwaysIgnore()
    try:
        osmo.generate()
    except:
        pass
    assert osmo.history.total_amount_of_steps == 10 * 100


def test_allow_count():
    osmo = Osmo(JustFailModel(AssertionError('Failing test_stop_on_failure')))
    osmo.test_end_condition = Length(10)
    osmo.test_suite_end_condition = Length(10)
    osmo.test_error_strategy = AllowCount(3)
    osmo.test_suite_error_strategy = AllowCount(3)
    try:
        osmo.generate()
    except:
        pass
    assert osmo.history.total_amount_of_steps == 3 + 1
