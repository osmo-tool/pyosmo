from pyosmo.error_strategy.base import OsmoErrorStrategy
from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel


class AlwaysRaise(OsmoErrorStrategy):
    """
    Just raise the exception always, which stops osmo execution
    """

    def failure_in_test(self, history: OsmoHistory, model: OsmoModel, error: Exception):
        raise error

    def failure_in_suite(self, history: OsmoHistory, model: OsmoModel, error: Exception):
        raise error
