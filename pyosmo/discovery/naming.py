"""Naming convention discovery strategy."""

import inspect

from pyosmo.discovery.base import DiscoveryStrategy, StepMetadata


class NamingConventionDiscovery(DiscoveryStrategy):
    """Discover steps via step_* naming convention.

    This strategy finds methods that follow the naming convention:
    - step_* for test steps
    - guard_* for guards
    - weight_* for weights

    It has lower priority than decorator-based discovery to allow
    decorators to override naming-based behavior.
    """

    def discover_steps(self, model: object) -> list[StepMetadata]:
        """Discover steps via naming convention.

        Args:
            model: Model instance to inspect

        Returns:
            List of step metadata for naming convention steps
        """
        steps = []

        for attr_name, method in inspect.getmembers(model, predicate=callable):
            # Skip private/protected methods
            if attr_name.startswith('_'):
                continue

            # Check for step_* naming convention
            if attr_name.startswith('step_'):
                # Extract step name (remove 'step_' prefix)
                step_name = attr_name[5:]

                steps.append(
                    StepMetadata(
                        name=step_name,
                        function_name=attr_name,
                        method=method,
                        is_decorator_based=False,
                        metadata={},
                    )
                )

        return steps

    def get_priority(self) -> int:
        """Naming convention discovery has lower priority (50)."""
        return 50
