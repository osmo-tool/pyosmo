# pylint: disable=too-few-public-methods
import logging
import random

from pyosmo.algorithm import RandomAlgorithm
from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.end_conditions.length import Length
from pyosmo.error_strategy.always_raise import AlwaysRaise
from pyosmo.error_strategy.base import OsmoErrorStrategy

logger = logging.getLogger('osmo')


class OsmoConfig:
    """ Osmo run configutaion object """

    def __init__(self):
        self._seed = random.randint(0, 10000)  # pragma: no mutate
        self._random = random.Random(self.seed)
        self._algorithm = RandomAlgorithm()
        self._test_end_condition = Length(10)
        self._test_suite_end_condition = Length(1)
        self._test_error_strategy = AlwaysRaise()
        self._test_suite_error_strategy = AlwaysRaise()

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        """ Set test generation algorithm """
        logger.debug("Set seed: {}".format(value))
        if not isinstance(value, int):
            raise AttributeError("config needs to be OsmoConfig.")
        self._seed = value
        self._random = random.Random(self._seed)

    @property
    def random(self):
        return self._random

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        """ Set test generation algorithm """
        if not isinstance(value, OsmoAlgorithm):
            raise AttributeError("algorithm needs to be OsmoAlgorithm")
        self._algorithm = value

    @property
    def test_end_condition(self):
        return self._test_end_condition

    @test_end_condition.setter
    def test_end_condition(self, value):
        """ Set test generation test_end_condition """
        if not isinstance(value, OsmoEndCondition):
            raise AttributeError("test_end_condition needs to be OsmoEndCondition")
        self._test_end_condition = value

    @property
    def test_suite_end_condition(self):
        return self._test_suite_end_condition

    @test_suite_end_condition.setter
    def test_suite_end_condition(self, value):
        """ Set test generation test_suite_end_condition """
        if not isinstance(value, OsmoEndCondition):
            raise AttributeError("test_suite_end_condition needs to be OsmoEndCondition")
        self._test_suite_end_condition = value

    @property
    def test_error_strategy(self):
        return self._test_error_strategy

    @test_error_strategy.setter
    def test_error_strategy(self, value):
        """ Set test generation test_suite_end_condition """
        if not isinstance(value, OsmoErrorStrategy):
            raise AttributeError("test_error_strategy needs to be OsmoErrorStrategy")
        self._test_error_strategy = value

    @property
    def test_suite_error_strategy(self):
        return self._test_suite_error_strategy

    @test_suite_error_strategy.setter
    def test_suite_error_strategy(self, value):
        """ Set test generation test_suite_end_condition """
        if not isinstance(value, OsmoErrorStrategy):
            raise AttributeError("test_suite_error_strategy needs to be OsmoErrorStrategy")
        self._test_suite_error_strategy = value
