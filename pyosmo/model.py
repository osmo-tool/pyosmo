import inspect
import logging
from collections.abc import Callable, Iterator
from typing import Any, Optional

logger = logging.getLogger('osmo')


class ModelFunction:
    """Generic function class containing basic functionality of model functions"""

    def __init__(self, function_name: str, object_instance: object) -> None:
        self.function_name = function_name
        self.object_instance = object_instance  # Instance of model class

    @property
    def default_weight(self) -> float:
        try:
            return float(self.object_instance.weight)  # type: ignore[attr-defined]
        except AttributeError:
            return 1.0  # Default weight of 1.0 for all steps

    @property
    def func(self) -> Callable[[], Any]:
        return getattr(self.object_instance, self.function_name)

    def execute(self) -> Any:
        try:
            return self.func()
        except AttributeError as e:
            raise Exception(f'Osmo cannot find function {self.object_instance}.{self.function_name} from model') from e

    def __str__(self) -> str:
        return f'{type(self.object_instance).__name__}.{self.function_name}()'


class TestStep(ModelFunction):
    def __init__(
        self,
        function_name: str,
        object_instance: object,
        step_name: str | None = None,
        is_decorator_based: bool = False,
    ) -> None:
        if not is_decorator_based:
            assert function_name.startswith('step_'), 'Wrong name function'
        super().__init__(function_name, object_instance)
        self._step_name = step_name
        self._is_decorator_based = is_decorator_based

    @property
    def name(self) -> str:
        """name means the part after 'step_' for naming convention or the explicit name for decorators"""
        if self._step_name:
            return self._step_name
        return self.function_name[5:]  # Remove 'step_' prefix

    @property
    def guard_name(self) -> str:
        return f'guard_{self.name}'

    @property
    def weight(self) -> float:
        # Check decorator-based weight first
        if hasattr(self.func, '_osmo_weight') and self.func._osmo_weight is not None:
            return float(self.func._osmo_weight)  # type: ignore[arg-type]

        # Check weight function (naming convention)
        weight_function = self.return_function_if_exists(f'weight_{self.name}')
        if weight_function is not None:
            return float(weight_function.execute())

        # Check weight attribute (legacy decorator)
        if hasattr(self.func, 'weight'):
            return float(self.func.weight)  # type: ignore[arg-type]

        return self.default_weight  # Default value

    @property
    def is_available(self) -> bool:
        """Check if step is available right now"""
        # Check if step is disabled by decorator
        if hasattr(self.func, '_osmo_enabled') and not self.func._osmo_enabled:
            return False

        # Check for inline guard (decorator-based)
        if hasattr(self.func, '_osmo_guard_inline'):
            result = bool(self.func._osmo_guard_inline(self.object_instance))  # type: ignore[operator]
            # Apply invert if specified
            if hasattr(self.func, '_osmo_guard_invert') and self.func._osmo_guard_invert:
                result = not result
            return result

        # Check for decorator-based guard (@guard("step_name"))
        decorator_guard = self._find_decorator_guard()
        if decorator_guard is not None:
            result = bool(decorator_guard.execute())
            # Check if guard should be inverted
            guard_func = decorator_guard.func
            if hasattr(guard_func, '_osmo_guard_invert') and guard_func._osmo_guard_invert:
                result = not result
            return result

        # Check for named guard function (naming convention)
        return True if self.guard_function is None else bool(self.guard_function.execute())

    def _find_decorator_guard(self) -> Optional['ModelFunction']:
        """Find a guard method decorated with @guard("step_name") for this step.

        Uses inspect.getmembers() for robust introspection.
        Supports both instance methods and static methods.
        """
        for attr_name, method in inspect.getmembers(self.object_instance, predicate=callable):
            # Skip private/protected methods
            if attr_name.startswith('_'):
                continue

            if (
                hasattr(method, '_osmo_guard')
                and hasattr(method, '_osmo_guard_for')
                and method._osmo_guard_for == self.name
            ):
                return ModelFunction(attr_name, self.object_instance)
        return None

    @property
    def guard_function(self) -> Optional['ModelFunction']:
        """Return guard function if it exists, otherwise None."""
        return self.return_function_if_exists(self.guard_name)

    def return_function_if_exists(self, name: str) -> Optional['ModelFunction']:
        """Return ModelFunction if method exists in the model instance, otherwise None.

        Uses hasattr() instead of dir() for robust attribute checking.
        """
        if hasattr(self.object_instance, name):
            attr = getattr(self.object_instance, name)
            if callable(attr):
                return ModelFunction(name, self.object_instance)
        return None


class OsmoModelCollector:
    """The whole model that osmo has in "mind" which may contain multiple partial models"""

    def __init__(self) -> None:
        # Format: functions[function_name] = link_of_instance
        self.sub_models: list[object] = []
        self.debug: bool = False
        # Performance optimization: cache discovered steps
        self._steps_cache: list[TestStep] | None = None
        self._cache_valid: bool = False

    def _discover_steps(self, sub_model: object) -> Iterator[TestStep]:
        """Discover steps using both naming convention and decorators.

        Uses inspect.getmembers() for robust introspection, avoiding
        fragile dir() patterns and properly handling inherited methods.
        Supports both instance methods and static methods.
        """
        discovered_step_names = set()

        # First, discover decorator-based steps
        for attr_name, method in inspect.getmembers(sub_model, predicate=callable):
            # Skip private/protected methods
            if attr_name.startswith('_'):
                continue

            if hasattr(method, '_osmo_step'):
                step_name = method._osmo_step_name  # type: ignore[attr-defined]
                discovered_step_names.add(attr_name)
                yield TestStep(attr_name, sub_model, step_name, is_decorator_based=True)

        # Then, discover naming convention steps (skip if already found via decorator)
        for attr_name, _method in inspect.getmembers(sub_model, predicate=callable):
            # Skip if already discovered or is private/protected
            if attr_name in discovered_step_names or attr_name.startswith('_'):
                continue

            if attr_name.startswith('step_'):
                yield TestStep(attr_name, sub_model)

    @property
    def all_steps(self) -> Iterator[TestStep]:
        """Get all discovered steps (with caching for performance).

        Steps are discovered once and cached until models are added/modified.
        This improves performance when repeatedly accessing all_steps.
        """
        if not self._cache_valid or self._steps_cache is None:
            # Rebuild cache
            self._steps_cache = [step for sub_model in self.sub_models for step in self._discover_steps(sub_model)]
            self._cache_valid = True

        return iter(self._steps_cache)

    def get_step_by_name(self, name: str) -> TestStep | None:
        """Get step by function name.

        Uses inspect.getmembers() for robust introspection.
        Supports both instance methods and static methods.
        """
        for sub_model in self.sub_models:
            for attr_name, _method in inspect.getmembers(sub_model, predicate=callable):
                if attr_name == name:
                    return TestStep(attr_name, sub_model)
        return None

    def functions_by_name(self, name: str) -> Iterator[ModelFunction]:
        """Get all functions with a specific name from all sub-models.

        Uses inspect.getmembers() for robust introspection.
        Supports both instance methods and static methods.
        """
        for sub_model in self.sub_models:
            for attr_name, _method in inspect.getmembers(sub_model, predicate=callable):
                if attr_name == name:
                    yield ModelFunction(attr_name, sub_model)

    def add_model(self, model: object) -> None:
        """Add model for osmo.

        Invalidates step cache since new model may add steps.
        """
        # Check if model is a class (not an instance) and instantiate it
        if inspect.isclass(model):
            model = model()

        self.sub_models.append(model)
        # Invalidate cache since we added a model
        self._cache_valid = False
        logger.debug(f'Loaded model: {model.__class__}')

    def execute_optional(self, function_name: str) -> None:
        """Execute all this name functions if available"""
        for function in self.functions_by_name(function_name):
            logger.debug(f'Execute: {function}')
            function.execute()

    @property
    def available_steps(self) -> list[TestStep]:
        """Return iterator for all available steps"""
        return [x for x in self.all_steps if x.is_available]
