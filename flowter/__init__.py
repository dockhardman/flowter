import inspect
import time
import uuid
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
        next_: Optional[Union["Node", List["Node"]]] = None,
    ):
        self.func = func
        self.func_signature = inspect.signature(self.func)
        if isinstance(next_, Node):
            next_ = [next_]
        self.next_: Optional[List[Node]] = next_ or None

        self.id = uuid.uuid4()

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)

    @property
    def func_params(self):
        return self.func_signature.parameters

    def add_next(self, next_: Union["Node", List["Node"]]):
        self.next_ = self.next_ or []
        self.next_.extend(self.validate_nodes(next_))

    @classmethod
    def validate_node(self, node: "Node", none_allowed: bool = False) -> "Node":
        if isinstance(node, Node):
            return node
        elif none_allowed and node is None:
            return node
        else:
            raise ValueError("The input node must be of type 'Node'")

    @classmethod
    def validate_nodes(self, nodes: Union["Node", List["Node"]]) -> List["Node"]:
        if isinstance(nodes, Node):
            nodes = [nodes]
        for n in nodes:
            try:
                self.validate_node(n)
            except ValueError:
                raise ValueError(
                    "The input nodes must be of type 'Node' but got: {type(n)}"
                )
        return nodes


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
