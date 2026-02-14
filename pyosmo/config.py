import logging
from random import Random, randint
from typing import Any

from pyosmo.algorithm import RandomAlgorithm
from pyosmo.algorithm.base import OsmoAlgorithm
from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.end_conditions.length import Length
from pyosmo.error_strategy.always_raise import AlwaysRaise
from pyosmo.error_strategy.base import OsmoErrorStrategy

logger = logging.getLogger('osmo')

# Default random seed range
DEFAULT_SEED_MAX = 10000


class ConfigurationError(ValueError):
    """Raised when configuration validation fails."""

    pass


class ConfigValidator:
    """Validates configuration values with comprehensive error messages."""

    @staticmethod
    def _validate_type(value: Any, expected_type: type, name: str, available: str) -> None:
        """Generic type validation for configuration values."""
        if value is None:
            raise ConfigurationError(
                f'{name} cannot be None. Please provide a valid {expected_type.__name__} instance.'
            )
        if not isinstance(value, expected_type):
            raise ConfigurationError(
                f'{name} must be an instance of {expected_type.__name__}, '
                f'got {type(value).__name__}. '
                f'Available: {available}.'
            )

    @staticmethod
    def validate_algorithm(algorithm: Any) -> None:
        ConfigValidator._validate_type(
            algorithm,
            OsmoAlgorithm,
            'Algorithm',
            'RandomAlgorithm, WeightedAlgorithm, BalancingAlgorithm',
        )

    @staticmethod
    def validate_end_condition(condition: Any, name: str = 'End condition') -> None:
        ConfigValidator._validate_type(
            condition,
            OsmoEndCondition,
            name,
            'Length, Time, StepCoverage, Endless, And, Or',
        )

    @staticmethod
    def validate_error_strategy(strategy: Any, name: str = 'Error strategy') -> None:
        ConfigValidator._validate_type(
            strategy,
            OsmoErrorStrategy,
            name,
            'AlwaysRaise, AlwaysIgnore, IgnoreAsserts, AllowCount',
        )

    @staticmethod
    def validate_seed(seed: Any) -> None:
        """Validate random seed value.

        Args:
            seed: Seed value to validate

        Raises:
            ConfigurationError: If seed is invalid
        """
        if not isinstance(seed, int):
            raise ConfigurationError(f'Seed must be an integer, got {type(seed).__name__}.')

        if seed < 0:
            raise ConfigurationError(f'Seed must be non-negative, got {seed}.')

        if seed > 2**32 - 1:
            raise ConfigurationError(
                f'Seed must fit in 32 bits (max {2**32 - 1}), got {seed}. Use a smaller seed value for reproducibility.'
            )


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
    def algorithm(self, value: OsmoAlgorithm) -> None:
        """Set test generation algorithm with validation.

        Args:
            value: Algorithm instance

        Raises:
            ConfigurationError: If algorithm is invalid
        """
        ConfigValidator.validate_algorithm(value)
        self._algorithm = value

    @property
    def test_end_condition(self) -> OsmoEndCondition:
        return self._test_end_condition

    @test_end_condition.setter
    def test_end_condition(self, value: OsmoEndCondition) -> None:
        """Set test end condition with validation.

        Args:
            value: End condition instance

        Raises:
            ConfigurationError: If end condition is invalid
        """
        ConfigValidator.validate_end_condition(value, 'Test end condition')
        self._test_end_condition = value

    @property
    def test_suite_end_condition(self) -> OsmoEndCondition:
        return self._test_suite_end_condition

    @test_suite_end_condition.setter
    def test_suite_end_condition(self, value: OsmoEndCondition) -> None:
        """Set test suite end condition with validation.

        Args:
            value: End condition instance

        Raises:
            ConfigurationError: If end condition is invalid
        """
        ConfigValidator.validate_end_condition(value, 'Test suite end condition')
        self._test_suite_end_condition = value

    @property
    def test_error_strategy(self) -> OsmoErrorStrategy:
        return self._test_error_strategy

    @test_error_strategy.setter
    def test_error_strategy(self, value: OsmoErrorStrategy) -> None:
        """Set test error strategy with validation.

        Args:
            value: Error strategy instance

        Raises:
            ConfigurationError: If error strategy is invalid
        """
        ConfigValidator.validate_error_strategy(value, 'Test error strategy')
        self._test_error_strategy = value

    @property
    def test_suite_error_strategy(self) -> OsmoErrorStrategy:
        return self._test_suite_error_strategy

    @test_suite_error_strategy.setter
    def test_suite_error_strategy(self, value: OsmoErrorStrategy) -> None:
        """Set test suite error strategy with validation.

        Args:
            value: Error strategy instance

        Raises:
            ConfigurationError: If error strategy is invalid
        """
        ConfigValidator.validate_error_strategy(value, 'Test suite error strategy')
        self._test_suite_error_strategy = value
