from pyosmo.error_strategy.base import OsmoErrorStrategy


class AlwaysIgnore(OsmoErrorStrategy):
    """
    Ignore assertion errors
    """

    def failure_in_test(self, history, model, error):
        if not isinstance(error, AssertionError):
            raise error

    def failure_in_suite(self, history, model, error):
        if not isinstance(error, AssertionError):
            raise error
