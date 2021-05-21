from pyosmo.error_strategy.base import OsmoErrorStrategy


class AlwaysRaise(OsmoErrorStrategy):
    """
    Just raise the exception always, which stops osmo execution
    """

    def failure_in_test(self, history, model, error):
        raise error

    def failure_in_suite(self, history, model, error):
        raise error
