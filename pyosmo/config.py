# pylint: disable=too-few-public-methods
from pyosmo.algorithm.random import RandomAlgorithm
from pyosmo.end_conditions.length import Length
from pyosmo.error_strategy.always_raise import AlwaysRaise


class OsmoConfig:
    """ Osmo run configutaion object """

    def __init__(self):
        self.algorithm = RandomAlgorithm()
        self.test_end_condition = Length(10)
        self.test_suite_end_condition = Length(1)
        self.test_failure_strategy = AlwaysRaise()
        self.test_suite_failure_strategy = AlwaysRaise()
