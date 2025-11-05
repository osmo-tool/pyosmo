from typing import Callable, TypeVar, Union

F = TypeVar('F', bound=Callable[..., object])


def weight(value: Union[int, float]) -> Callable[[F], F]:
    """Make able to put weight in classes or functions by decorator @weight"""

    def decorator(func: F) -> F:
        func.weight = value  # type: ignore[attr-defined]
        return func

    return decorator
