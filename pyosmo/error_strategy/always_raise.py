from pyosmo.error_strategy.base import OsmoErrorStrategy
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class AlwaysRaise(OsmoErrorStrategy):
    """
    Just raise the exception always, which stops osmo execution
    """

    def failure_in_test(self, history: OsmoHistory, model: OsmoModelCollector, error: Exception):
        raise error

    def failure_in_suite(self, history: OsmoHistory, model: OsmoModelCollector, error: Exception):
        raise error
