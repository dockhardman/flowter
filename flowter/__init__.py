import time
from functools import wraps
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

from .version import VERSION

__version__ = VERSION

T = TypeVar("T")
P = ParamSpec("P")


class flow:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*inner_args: P.args, **inner_kwargs: P.kwargs) -> T:
            start = time.time()
            result = func(*inner_args, **inner_kwargs)
            end = time.time()
            print(f"{func.__name__} took {end-start:.2f} seconds to run.")
            return result

        return wrapper
