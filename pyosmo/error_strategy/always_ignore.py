from pyosmo.error_strategy.base import OsmoErrorStrategy


class AlwaysIgnore(OsmoErrorStrategy):
    """
    Ignore failures every time
    """

    def failure_in_test(self, history, model, error):
        pass

    def failure_in_suite(self, history, model, error):
        pass
