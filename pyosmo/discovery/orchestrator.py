"""Discovery orchestrator that combines multiple strategies."""

from pyosmo.discovery.base import DiscoveryStrategy, ModelMetadata, StepMetadata
from pyosmo.discovery.decorator import DecoratorBasedDiscovery
from pyosmo.discovery.naming import NamingConventionDiscovery


class ModelDiscovery:
    """Orchestrates multiple discovery strategies.

    This class manages multiple discovery strategies and combines their
    results, handling deduplication and priority ordering.
    """

    def __init__(self, strategies: list[DiscoveryStrategy] | None = None):
        """Initialize with discovery strategies.

        Args:
            strategies: List of discovery strategies. If None, uses default
                       strategies (decorator-based and naming convention).
        """
        if strategies is None:
            strategies = [
                DecoratorBasedDiscovery(),
                NamingConventionDiscovery(),
            ]

        # Sort strategies by priority (lower number = higher priority)
        self.strategies = sorted(strategies, key=lambda s: s.get_priority())

    def discover(self, model: object) -> ModelMetadata:
        """Discover all model components using all strategies.

        Args:
            model: Model instance to inspect

        Returns:
            ModelMetadata with all discovered steps
        """
        all_steps: list[StepMetadata] = []
        seen_names: set[str] = set()

        # Run strategies in priority order
        for strategy in self.strategies:
            steps = strategy.discover_steps(model)

            for step in steps:
                # Skip if we've already found this step (higher priority strategy won)
                if step.function_name not in seen_names:
                    all_steps.append(step)
                    seen_names.add(step.function_name)

        return ModelMetadata(steps=all_steps, model=model)

    def add_strategy(self, strategy: DiscoveryStrategy) -> None:
        """Add a new discovery strategy.

        Args:
            strategy: Discovery strategy to add
        """
        self.strategies.append(strategy)
        # Re-sort by priority
        self.strategies.sort(key=lambda s: s.get_priority())
