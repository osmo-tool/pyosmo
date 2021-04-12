from pyosmo.algorithm.random import RandomAlgorithm
from pyosmo.end_conditions.length import Length


class OsmoConfig(object):
    """ Osmo run configutaion object """
    def __init__(self):
        self.stop_on_fail = True
        self.algorithm = RandomAlgorithm()
        self.stop_test_on_exception = True
        self.test_end_condition = Length(10)
        self.test_suite_end_condition = Length(1)
