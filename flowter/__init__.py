import inspect
import time
import uuid
from functools import wraps
from typing import Callable, Dict, List, Optional, TypeVar, Union

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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Node):
            return self.id == __value.id
        else:
            return False

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)

    @property
    def func_params(self):
        return self.func_signature.parameters

    def add_next(self, next_: Union["Node", List["Node"]]):
        self.next_ = self.next_ or []
        for n in self.validate_nodes(next_):
            if n not in self.next_:
                self.next_.append(n)

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

        self.node_pool: Dict[uuid.UUID, Node] = {}

    def add_node(
        self,
        n: Callable[P, T],
        src: Optional[Node] = None,
        dst: Optional[Node] = None,
    ) -> Node:
        src = Node.validate_node(src, none_allowed=True)
        node = (
            n
            if isinstance(n, Node)
            else Node(n, next_=Node.validate_node(dst, none_allowed=True))
        )
        self.node_pool[node.id] = node
        if src:
            src.add_next(node)
            self.node_pool[src.id] = src
        if dst:
            self.node_pool[dst.id] = dst
        return node
