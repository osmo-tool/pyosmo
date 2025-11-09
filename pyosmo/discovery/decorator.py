"""Decorator-based discovery strategy."""

import inspect

from pyosmo.discovery.base import DiscoveryStrategy, StepMetadata


class DecoratorBasedDiscovery(DiscoveryStrategy):
    """Discover steps via @step, @guard decorators.

    This strategy finds methods decorated with @step and extracts
    their metadata. It has higher priority than naming convention
    to allow explicit override of naming-based discovery.
    """

    def discover_steps(self, model: object) -> list[StepMetadata]:
        """Discover steps via decorators.

        Args:
            model: Model instance to inspect

        Returns:
            List of step metadata for decorator-based steps
        """
        steps = []

        for attr_name, method in inspect.getmembers(model, predicate=callable):
            # Skip private/protected methods
            if attr_name.startswith('_'):
                continue

            # Check for @step decorator
            if hasattr(method, '_osmo_step'):
                step_name = getattr(method, '_osmo_step_name', attr_name)
                metadata = getattr(method, '_osmo_metadata', {})

                steps.append(
                    StepMetadata(
                        name=step_name,
                        function_name=attr_name,
                        method=method,
                        is_decorator_based=True,
                        metadata=metadata,
                    )
                )

        return steps

    def get_priority(self) -> int:
        """Decorator-based discovery has high priority (10)."""
        return 10
