import inspect
import time
from functools import wraps
from typing import Callable, List, Optional, TypeVar, Union

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


class Node:
    def __init__(
        self,
        func: Callable[P, T],
        next_nodes: Optional[Union["Node", List["Node"]]] = None,
    ):
        self.func = func
        self.func_signature = inspect.signature(self.func)
        if isinstance(next_nodes, Node):
            next_nodes = [next_nodes]
        self.next_nodes: Optional[List[Node]] = next_nodes or None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)

    @property
    def func_params(self):
        return self.func_signature.parameters

    def add_next(self, next_node: "Node"):
        if not isinstance(next_node, Node):
            raise ValueError("The next_node must be of type 'Node'")
        if self.next_nodes is None:
            self.next_nodes = [next_node]
        else:
            self.next_nodes.append(next_node)


class FLow:
    def __init__(self, *args, **kwargs):
        self.start_node: Node = Node(lambda: None)
        self.end_node: Node = Node(lambda: None)

    def add_func(self, func: Callable[P, T], src: Optional[Node] = None) -> Node:
        node = Node(func, next_nodes=self.end_node)
        if src.next_nodes is None:
            src.next_nodes = [node]
        else:
            src.next_nodes.append(node)
        return node
