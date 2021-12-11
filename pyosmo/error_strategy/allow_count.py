from pyosmo.error_strategy.base import OsmoErrorStrategy
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class AllowCount(OsmoErrorStrategy):
    """
    Allow x amount of errors, then raise
    """

    def __init__(self, allow_count: int):
        self.allow_count = allow_count

    def failure_in_test(self, history: OsmoHistory, model: OsmoModelCollector, error: Exception):
        if history.current_test_case.error_count > self.allow_count:
            raise error

    def failure_in_suite(self, history: OsmoHistory, model: OsmoModelCollector, error: Exception):
        if history.error_count > self.allow_count:
            raise error
