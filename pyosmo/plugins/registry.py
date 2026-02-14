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
        self._registries: dict[str, dict[str, tuple[type[Any], str]]] = {
            'algorithm': {},
            'end_condition': {},
            'error_strategy': {},
        }

    def _register(
        self,
        kind: str,
        name: str,
        cls: type[Any],
        base_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        registry = self._registries[kind]
        if name in registry and not replace:
            raise PluginError(
                f"{kind.replace('_', ' ').title()} '{name}' already registered. Use replace=True to override."
            )
        if not (isinstance(cls, type) and issubclass(cls, base_class)):
            raise PluginError(f'{kind.replace("_", " ").title()} class must extend {base_class.__name__}, got {cls}')
        registry[name] = (cls, description)
        logger.debug(f'Registered {kind.replace("_", " ")}: {name}')

    def _get(self, kind: str, name: str) -> type[Any]:
        registry = self._registries[kind]
        if name not in registry:
            available = ', '.join(sorted(registry.keys()))
            raise PluginError(f"{kind.replace('_', ' ').title()} '{name}' not found. Available: {available or 'none'}")
        return registry[name][0]

    def _list(self, kind: str) -> dict[str, str]:
        return {name: desc for name, (_, desc) in self._registries[kind].items()}

    def register_algorithm(
        self,
        name: str,
        algorithm_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        from pyosmo.algorithm.base import OsmoAlgorithm

        self._register('algorithm', name, algorithm_class, OsmoAlgorithm, description=description, replace=replace)

    def register_end_condition(
        self,
        name: str,
        condition_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        from pyosmo.end_conditions.base import OsmoEndCondition

        self._register(
            'end_condition', name, condition_class, OsmoEndCondition, description=description, replace=replace
        )

    def register_error_strategy(
        self,
        name: str,
        strategy_class: type[Any],
        *,
        description: str = '',
        replace: bool = False,
    ) -> None:
        from pyosmo.error_strategy.base import OsmoErrorStrategy

        self._register(
            'error_strategy', name, strategy_class, OsmoErrorStrategy, description=description, replace=replace
        )

    def get_algorithm(self, name: str) -> type[Any]:
        return self._get('algorithm', name)

    def get_end_condition(self, name: str) -> type[Any]:
        return self._get('end_condition', name)

    def get_error_strategy(self, name: str) -> type[Any]:
        return self._get('error_strategy', name)

    def list_algorithms(self) -> dict[str, str]:
        return self._list('algorithm')

    def list_end_conditions(self) -> dict[str, str]:
        return self._list('end_condition')

    def list_error_strategies(self) -> dict[str, str]:
        return self._list('error_strategy')


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
