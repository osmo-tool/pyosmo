import logging
from random import Random, randint

from pyosmo.algorithm import RandomAlgorithm
from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.end_conditions.length import Length
from pyosmo.error_strategy.always_raise import AlwaysRaise
from pyosmo.error_strategy.base import OsmoErrorStrategy

logger = logging.getLogger('osmo')

# Default random seed range
DEFAULT_SEED_MAX = 10000


class OsmoConfig:
    """Osmo run configuration object"""

    def __init__(self) -> None:
        self._seed: int = randint(0, DEFAULT_SEED_MAX)  # pragma: no mutate
        self._random: Random = Random(self._seed)
        self._algorithm: OsmoAlgorithm = RandomAlgorithm()
        self._test_end_condition: OsmoEndCondition = Length(10)  # pragma: no mutate
        self._test_suite_end_condition: OsmoEndCondition = Length(1)  # pragma: no mutate
        self._test_error_strategy: OsmoErrorStrategy = AlwaysRaise()
        self._test_suite_error_strategy: OsmoErrorStrategy = AlwaysRaise()

    @property
    def random(self) -> Random:
        return self._random

    @property
    def algorithm(self) -> OsmoAlgorithm:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: OsmoAlgorithm):
        """Set test generation algorithm"""
        if not isinstance(value, OsmoAlgorithm):
            raise AttributeError('algorithm needs to be OsmoAlgorithm')
        self._algorithm = value

    @property
    def test_end_condition(self) -> OsmoEndCondition:
        return self._test_end_condition

    @test_end_condition.setter
    def test_end_condition(self, value: OsmoEndCondition):
        """Set test generation test_end_condition"""
        if not isinstance(value, OsmoEndCondition):
            raise AttributeError('test_end_condition needs to be OsmoEndCondition')
        self._test_end_condition = value

    @property
    def test_suite_end_condition(self) -> OsmoEndCondition:
        return self._test_suite_end_condition

    @test_suite_end_condition.setter
    def test_suite_end_condition(self, value: OsmoEndCondition):
        """Set test generation test_suite_end_condition"""
        if not isinstance(value, OsmoEndCondition):
            raise AttributeError('test_suite_end_condition needs to be OsmoEndCondition')
        self._test_suite_end_condition = value

    @property
    def test_error_strategy(self) -> OsmoErrorStrategy:
        return self._test_error_strategy

    @test_error_strategy.setter
    def test_error_strategy(self, value: OsmoErrorStrategy):
        """Set test generation test_suite_end_condition"""
        if not isinstance(value, OsmoErrorStrategy):
            raise AttributeError('test_error_strategy needs to be OsmoErrorStrategy')
        self._test_error_strategy = value

    @property
    def test_suite_error_strategy(self) -> OsmoErrorStrategy:
        return self._test_suite_error_strategy

    @test_suite_error_strategy.setter
    def test_suite_error_strategy(self, value: OsmoErrorStrategy):
        """Set test generation test_suite_end_condition"""
        if not isinstance(value, OsmoErrorStrategy):
            raise AttributeError('test_suite_error_strategy needs to be OsmoErrorStrategy')
        self._test_suite_error_strategy = value
