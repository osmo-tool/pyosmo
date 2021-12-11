from pyosmo.error_strategy.base import OsmoErrorStrategy
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class AlwaysIgnore(OsmoErrorStrategy):
    """
    Ignore failures every time
    """

    def failure_in_test(self, history: OsmoHistory, model: OsmoModelCollector, error: Exception):
        pass

    def failure_in_suite(self, history: OsmoHistory, model: OsmoModelCollector, error: Exception):
        pass
