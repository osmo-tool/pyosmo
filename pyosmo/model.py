import inspect
import logging
from typing import Any, Callable, Iterator, List, Optional

logger = logging.getLogger("osmo")


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
            return 0.0

    @property
    def func(self) -> Callable[[], Any]:
        return getattr(self.object_instance, self.function_name)  # type: ignore[no-any-return]

    def execute(self) -> Any:
        try:
            return self.func()
        except AttributeError as e:
            raise Exception(f"Osmo cannot find function {self.object_instance}.{self.function_name} from model") from e

    def __str__(self) -> str:
        return f"{type(self.object_instance).__name__}.{self.function_name}()"


class TestStep(ModelFunction):
    def __init__(self, function_name: str, object_instance: object) -> None:
        assert function_name.startswith("step_"), "Wrong name function"
        super().__init__(function_name, object_instance)

    @property
    def name(self) -> str:
        """name means the part after 'step_'"""
        return self.function_name[5:]

    @property
    def guard_name(self) -> str:
        return f"guard_{self.name}"

    @property
    def weight(self) -> float:
        weight_function = self.return_function_if_exists(f"weight_{self.name}")
        if weight_function is not None:
            return float(weight_function.execute())
        if "weight" in dir(self.func):
            return float(self.func.weight)  # type: ignore[attr-defined]
        return self.default_weight  # Default value

    @property
    def is_available(self) -> bool:
        """Check if step is available right now"""
        return True if self.guard_function is None else bool(self.guard_function.execute())

    @property
    def guard_function(self) -> Optional["ModelFunction"]:
        """Return guard function if it exists, otherwise None."""
        return self.return_function_if_exists(self.guard_name)

    def return_function_if_exists(self, name: str) -> Optional["ModelFunction"]:
        """Return ModelFunction if method exists in the model instance, otherwise None."""
        if name in dir(self.object_instance):
            return ModelFunction(name, self.object_instance)
        return None


class OsmoModelCollector:
    """The whole model that osmo has in "mind" which may contain multiple partial models"""

    def __init__(self) -> None:
        # Format: functions[function_name] = link_of_instance
        self.sub_models: List[object] = []
        self.debug: bool = False

    @property
    def all_steps(self) -> Iterator[TestStep]:
        return (
            TestStep(f, sub_model)
            for sub_model in self.sub_models
            for f in dir(sub_model)
            if callable(getattr(sub_model, f)) and f.startswith("step_")
        )

    def get_step_by_name(self, name: str) -> Optional[TestStep]:
        """Get step by function name"""
        steps = (
            TestStep(f, sub_model)
            for sub_model in self.sub_models
            for f in dir(sub_model)
            if callable(getattr(sub_model, f)) and f == name
        )
        for step in steps:
            return step
        return None  # noqa

    def functions_by_name(self, name: str) -> Iterator[ModelFunction]:
        return (
            ModelFunction(f, sub_model)
            for sub_model in self.sub_models
            for f in dir(sub_model)
            if callable(getattr(sub_model, f)) and f == name
        )

    def add_model(self, model: object) -> None:
        """Add model for osmo"""
        # Check if model is a class (not an instance) and instantiate it
        if inspect.isclass(model):
            model = model()

        self.sub_models.append(model)
        logger.debug(f"Loaded model: {model.__class__}")

    def execute_optional(self, function_name: str) -> None:
        """Execute all this name functions if available"""
        for function in self.functions_by_name(function_name):
            logger.debug(f"Execute: {function}")
            function.execute()

    @property
    def available_steps(self) -> List[TestStep]:
        """Return iterator for all available steps"""
        return list(filter(lambda x: x.is_available, self.all_steps))
