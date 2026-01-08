"""Central registry for all plugins."""

import logging
from typing import Any

logger = logging.getLogger('osmo')


class PluginError(Exception):
    """Raised when plugin registration or retrieval fails."""

    pass


class PluginRegistry:
    """Central registry for all PyOsmo plugins.

    This registry maintains collections of algorithms, end conditions,
    and error strategies, enabling discoverability and extensibility.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._algorithms: dict[str, tuple[type[Any], str]] = {}
        self._end_conditions: dict[str, tuple[type[Any], str]] = {}
        self._error_strategies: dict[str, tuple[type[Any], str]] = {}

    def register_algorithm(
        self,
        name: str,
        algorithm_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        """Register a test generation algorithm.

        Args:
            name: Unique name for this algorithm
            algorithm_class: Algorithm class to register
            description: Human-readable description
            replace: If True, replace existing registration (default: False)

        Raises:
            PluginError: If name already registered and replace=False
        """
        if name in self._algorithms and not replace:
            raise PluginError(f"Algorithm '{name}' already registered. Use replace=True to override.")

        from pyosmo.algorithm.base import OsmoAlgorithm

        if not (isinstance(algorithm_class, type) and issubclass(algorithm_class, OsmoAlgorithm)):
            raise PluginError(f'Algorithm class must extend OsmoAlgorithm, got {algorithm_class}')

        self._algorithms[name] = (algorithm_class, description)
        logger.debug(f'Registered algorithm: {name}')

    def register_end_condition(
        self,
        name: str,
        condition_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        """Register an end condition.

        Args:
            name: Unique name for this condition
            condition_class: End condition class to register
            description: Human-readable description
            replace: If True, replace existing registration (default: False)

        Raises:
            PluginError: If name already registered and replace=False
        """
        if name in self._end_conditions and not replace:
            raise PluginError(f"End condition '{name}' already registered. Use replace=True to override.")

        from pyosmo.end_conditions.base import OsmoEndCondition

        if not (isinstance(condition_class, type) and issubclass(condition_class, OsmoEndCondition)):
            raise PluginError(f'End condition class must extend OsmoEndCondition, got {condition_class}')

        self._end_conditions[name] = (condition_class, description)
        logger.debug(f'Registered end condition: {name}')

    def register_error_strategy(
        self,
        name: str,
        strategy_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        """Register an error strategy.

        Args:
            name: Unique name for this strategy
            strategy_class: Error strategy class to register
            description: Human-readable description
            replace: If True, replace existing registration (default: False)

        Raises:
            PluginError: If name already registered and replace=False
        """
        if name in self._error_strategies and not replace:
            raise PluginError(f"Error strategy '{name}' already registered. Use replace=True to override.")

        from pyosmo.error_strategy.base import OsmoErrorStrategy

        if not (isinstance(strategy_class, type) and issubclass(strategy_class, OsmoErrorStrategy)):
            raise PluginError(f'Error strategy class must extend OsmoErrorStrategy, got {strategy_class}')

        self._error_strategies[name] = (strategy_class, description)
        logger.debug(f'Registered error strategy: {name}')

    def get_algorithm(self, name: str) -> type[Any]:
        """Get algorithm class by name.

        Args:
            name: Algorithm name

        Returns:
            Algorithm class

        Raises:
            PluginError: If algorithm not found
        """
        if name not in self._algorithms:
            available = ', '.join(sorted(self._algorithms.keys()))
            raise PluginError(f"Algorithm '{name}' not found. Available: {available or 'none'}")
        return self._algorithms[name][0]

    def get_end_condition(self, name: str) -> type[Any]:
        """Get end condition class by name.

        Args:
            name: End condition name

        Returns:
            End condition class

        Raises:
            PluginError: If end condition not found
        """
        if name not in self._end_conditions:
            available = ', '.join(sorted(self._end_conditions.keys()))
            raise PluginError(f"End condition '{name}' not found. Available: {available or 'none'}")
        return self._end_conditions[name][0]

    def get_error_strategy(self, name: str) -> type[Any]:
        """Get error strategy class by name.

        Args:
            name: Error strategy name

        Returns:
            Error strategy class

        Raises:
            PluginError: If error strategy not found
        """
        if name not in self._error_strategies:
            available = ', '.join(sorted(self._error_strategies.keys()))
            raise PluginError(f"Error strategy '{name}' not found. Available: {available or 'none'}")
        return self._error_strategies[name][0]

    def list_algorithms(self) -> dict[str, str]:
        """List all registered algorithms with descriptions.

        Returns:
            Dict mapping algorithm names to descriptions
        """
        return {name: desc for name, (_, desc) in self._algorithms.items()}

    def list_end_conditions(self) -> dict[str, str]:
        """List all registered end conditions with descriptions.

        Returns:
            Dict mapping end condition names to descriptions
        """
        return {name: desc for name, (_, desc) in self._end_conditions.items()}

    def list_error_strategies(self) -> dict[str, str]:
        """List all registered error strategies with descriptions.

        Returns:
            Dict mapping error strategy names to descriptions
        """
        return {name: desc for name, (_, desc) in self._error_strategies.items()}


# Global registry instance
_global_registry: PluginRegistry | None = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry.

    Returns:
        The global PluginRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
        # Register built-in plugins
        _register_builtin_plugins(_global_registry)
    return _global_registry


def _register_builtin_plugins(registry: PluginRegistry) -> None:
    """Register built-in algorithms, end conditions, and error strategies.

    Args:
        registry: Registry to populate
    """
    # Register built-in algorithms
    from pyosmo.algorithm import BalancingAlgorithm, RandomAlgorithm, WeightedAlgorithm

    registry.register_algorithm(
        'random',
        RandomAlgorithm,
        description='Purely random step selection',
    )
    registry.register_algorithm(
        'weighted',
        WeightedAlgorithm,
        description='Weight-based random selection',
    )
    registry.register_algorithm(
        'balancing',
        BalancingAlgorithm,
        description='Coverage-balancing algorithm',
    )

    # Register built-in end conditions
    from pyosmo.end_conditions import Endless, Length, StepCoverage, Time

    registry.register_end_condition(
        'length',
        Length,
        description='Stop after N steps',
    )
    registry.register_end_condition(
        'time',
        Time,
        description='Stop after elapsed time',
    )
    registry.register_end_condition(
        'coverage',
        StepCoverage,
        description='Stop when coverage threshold reached',
    )
    registry.register_end_condition(
        'endless',
        Endless,
        description='Run forever (online testing)',
    )

    # Register built-in error strategies
    from pyosmo.error_strategy import (
        AllowCount,
        AlwaysIgnore,
        AlwaysRaise,
        IgnoreAsserts,
    )

    registry.register_error_strategy(
        'raise',
        AlwaysRaise,
        description='Fail fast on any error',
    )
    registry.register_error_strategy(
        'ignore',
        AlwaysIgnore,
        description='Continue on all errors',
    )
    registry.register_error_strategy(
        'ignore_asserts',
        IgnoreAsserts,
        description='Ignore assertion errors only',
    )
    registry.register_error_strategy(
        'allow_count',
        AllowCount,
        description='Allow up to N errors',
    )


def register_algorithm(name: str, description: str = '') -> Any:
    """Decorator to register an algorithm with the global registry.

    Args:
        name: Unique name for the algorithm
        description: Human-readable description

    Returns:
        Decorator function

    Example:
        @register_algorithm("my_algo", "Custom algorithm")
        class MyAlgorithm(OsmoAlgorithm):
            ...
    """

    def decorator(cls: type[Any]) -> type[Any]:
        get_registry().register_algorithm(name, cls, description=description)
        return cls

    return decorator
