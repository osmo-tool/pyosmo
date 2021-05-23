from pyosmo.error_strategy.base import OsmoErrorStrategy


class AllowCount(OsmoErrorStrategy):
    """
    Allow x amount of errors, then raise
    """

    def __init__(self, allow_count):
        self.allow_count = allow_count

    def failure_in_test(self, history, model, error):
        if history.current_test_case.error_count > self.allow_count:
            raise error

    def failure_in_suite(self, history, model, error):
        if history.error_count > self.allow_count:
            raise error
