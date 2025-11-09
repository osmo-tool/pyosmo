"""Base classes for model discovery strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepMetadata:
    """Metadata for a discovered test step."""

    name: str  # Step name (without 'step_' prefix)
    function_name: str  # Full function name
    method: Any  # The actual method object
    is_decorator_based: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetadata:
    """Complete metadata for a discovered model."""

    steps: list[StepMetadata]
    model: object

    def get_step_names(self) -> list[str]:
        """Get list of step names."""
        return [step.name for step in self.steps]

    def get_step_by_name(self, name: str) -> StepMetadata | None:
        """Get step metadata by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None


class DiscoveryStrategy(ABC):
    """Base class for model discovery strategies.

    Discovery strategies are responsible for finding test steps,
    guards, and weights in model classes using different mechanisms
    (naming conventions, decorators, annotations, etc.).
    """

    @abstractmethod
    def discover_steps(self, model: object) -> list[StepMetadata]:
        """Discover test steps in the model.

        Args:
            model: Model instance to inspect

        Returns:
            List of discovered step metadata
        """
        pass

    def get_priority(self) -> int:
        """Get priority for this discovery strategy.

        Lower numbers = higher priority (checked first).
        Default is 100.

        Returns:
            Priority value
        """
        return 100
