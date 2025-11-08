from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# Legacy weight decorator (kept for backward compatibility)
def weight(value: int | float) -> Callable[[F], F]:
    """Make able to put weight in classes or functions by decorator @weight"""

    def decorator(func: F) -> F:
        func.weight = value  # type: ignore[attr-defined]
        return func

    return decorator


# New decorator-based API


class StepDecorator:
    """Decorator for marking test steps."""

    def __init__(
        self, name: str | None = None, *, weight_value: int | float | None = None, enabled: bool = True
    ) -> None:
        self.name = name
        self.weight_value = weight_value
        self.enabled = enabled

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Attach metadata
        wrapper._osmo_step = True  # type: ignore[attr-defined]
        wrapper._osmo_step_name = self.name or func.__name__  # type: ignore[attr-defined]
        wrapper._osmo_weight = self.weight_value  # type: ignore[attr-defined]
        wrapper._osmo_enabled = self.enabled  # type: ignore[attr-defined]

        return wrapper


def step(
    name_or_func: str | Callable[..., Any] | None = None,
    *,
    weight_value: int | float | None = None,
    enabled: bool = True,
) -> Callable[..., Any] | StepDecorator:
    """Mark a method as a test step.

    Can be used with or without arguments:

        @step
        def my_step(self): pass

        @step("custom_name")
        def my_step(self): pass

        @step(weight_value=10, enabled=False)
        def my_step(self): pass

    Args:
        name_or_func: Step name or function (for no-arg usage)
        weight_value: Static weight for this step
        enabled: Whether step is enabled

    Returns:
        Decorated function or decorator
    """
    if callable(name_or_func):
        # Used without arguments: @step
        return StepDecorator()(name_or_func)
    # Used with arguments: @step("name")
    return StepDecorator(name_or_func, weight_value=weight_value, enabled=enabled)


def guard(step_name_or_func: str | Callable[..., Any], *, invert: bool = False) -> Callable[..., Any]:
    """Mark a method as a guard for a step.

    Can be used as inline lambda or separate method:

        @step
        @guard(lambda self: self.ready)
        def process(self): pass

        @guard("process")
        def can_process(self) -> bool:
            return self.ready

    Args:
        step_name_or_func: Step name or guard function
        invert: Invert guard logic (step enabled when False)

    Returns:
        Decorated function
    """
    if callable(step_name_or_func):
        # Inline guard
        func = step_name_or_func
        func._osmo_guard_inline = True  # type: ignore[attr-defined]
        func._osmo_guard_invert = invert  # type: ignore[attr-defined]
        return func

    # Named guard
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._osmo_guard = True  # type: ignore[attr-defined]
        func._osmo_guard_for = step_name_or_func  # type: ignore[attr-defined]
        func._osmo_guard_invert = invert  # type: ignore[attr-defined]
        return func

    return decorator


def pre(step_name: str) -> Callable[[F], F]:
    """Mark a method as a pre-step hook.

    Example:
        @pre("login")
        def before_login(self):
            print("About to log in")

    Args:
        step_name: Name of the step this hook should run before

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        func._osmo_pre = True  # type: ignore[attr-defined]
        func._osmo_pre_for = step_name  # type: ignore[attr-defined]
        return func

    return decorator


def post(step_name: str) -> Callable[[F], F]:
    """Mark a method as a post-step hook.

    Example:
        @post("login")
        def after_login(self):
            print("Logged in successfully")

    Args:
        step_name: Name of the step this hook should run after

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        func._osmo_post = True  # type: ignore[attr-defined]
        func._osmo_post_for = step_name  # type: ignore[attr-defined]
        return func

    return decorator


def requires(*requirements: str) -> Callable[[F], F]:
    """Mark a step as satisfying one or more requirements.

    Example:
        @step
        @requires("REQ-101", "REQ-102")
        def checkout(self):
            pass

    Args:
        requirements: Requirement IDs this step satisfies

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        func._osmo_requires = list(requirements)  # type: ignore[attr-defined]
        return func

    return decorator


def requires_all(*requirements: str) -> Callable[[F], F]:
    """Mark a step as satisfying all given requirements.

    Example:
        @step
        @requires_all("REQ-101", "REQ-102")
        def complete_order(self):
            pass

    Args:
        requirements: Requirement IDs this step satisfies

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        func._osmo_requires = list(requirements)  # type: ignore[attr-defined]
        func._osmo_requires_all = True  # type: ignore[attr-defined]
        return func

    return decorator


def requires_any(*requirements: str) -> Callable[[F], F]:
    """Mark a step as satisfying any of the given requirements.

    Example:
        @step
        @requires_any("REQ-101", "REQ-102")
        def check_auth(self):
            pass

    Args:
        requirements: Requirement IDs (any one) this step satisfies

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        func._osmo_requires = list(requirements)  # type: ignore[attr-defined]
        func._osmo_requires_any = True  # type: ignore[attr-defined]
        return func

    return decorator


def variable(name: str, categories: list[str] | None = None) -> Callable[[F], F]:
    """Mark a method as a variable provider for coverage tracking.

    Example:
        @variable("cart_size", categories=["empty", "small", "large"])
        def get_cart_size(self) -> str:
            if len(self.cart) == 0:
                return "empty"
            # ...

    Args:
        name: Variable name
        categories: Optional list of expected categories/values

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        func._osmo_variable = True  # type: ignore[attr-defined]
        func._osmo_variable_name = name  # type: ignore[attr-defined]
        func._osmo_variable_categories = categories  # type: ignore[attr-defined]
        return func

    return decorator


def state(func: F) -> F:
    """Mark a method as a state-providing function.

    Example:
        @state
        def get_state(self) -> str:
            return f"cart={len(self.cart)},user={self.user_id}"

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    func._osmo_state = True  # type: ignore[attr-defined]
    return func
