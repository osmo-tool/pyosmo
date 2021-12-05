from pyosmo.error_strategy.base import OsmoErrorStrategy
from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel


class IgnoreAsserts(OsmoErrorStrategy):
    """
    Ignore assertion errors
    """

    def failure_in_test(self, history: OsmoHistory, model: OsmoModel, error: Exception):
        if not isinstance(error, AssertionError):
            raise error

    def failure_in_suite(self, history: OsmoHistory, model: OsmoModel, error: Exception):
        if not isinstance(error, AssertionError):
            raise error
