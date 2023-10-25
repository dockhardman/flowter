import inspect
import time
import uuid
from functools import wraps
from typing import (
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Text,
    TypedDict,
    TypeVar,
    Union,
)

import rich
from typing_extensions import ParamSpec

from .helper import able_to_dict, collect_params, rand_str, str_or_none, validate_name
from .version import VERSION

__version__ = VERSION

T = TypeVar("T")
P = ParamSpec("P")

console = rich.get_console()


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


class Node(Generic[P, T]):
    def __init__(
        self,
        func: Callable[P, T],
        *args,
        name: Optional[Text] = None,
        next_: Optional[Union["Node", List["Node"]]] = None,
        return_envelope: Optional[Union[bool, Text]] = None,
        **kwargs,
    ):
        self.func = func
        self.func_signature = inspect.signature(self.func)
        if isinstance(next_, Node):
            next_ = [next_]
        self.name = validate_name(
            str_or_none(name) or f"{self.func.__name__}:{rand_str()}"
        )
        self.next_: Optional[List[Node]] = next_ or None
        self.return_envelope = return_envelope

        self.id = str(uuid.uuid4())

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Node):
            return self.id == __value.id
        else:
            return False

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)

    def __repr__(self) -> Text:
        return f"<Node id={self.id}, name={self.name}>"

    def __str__(self) -> Text:
        return self.__repr__()

    @property
    def func_params(self):
        return self.func_signature.parameters

    def run(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self(*args, **kwargs)

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


class Condition(Node[P, T]):
    pass


class Fork(Node[P, T]):
    pass


class Merge(Node[P, T]):
    pass


class Flow:
    class FlowRunResult(TypedDict):
        pass

    def __init__(
        self,
        *args,
        start_node: Optional[Node] = None,
        end_node: Optional[Node] = None,
        name: Optional[Text] = None,
        **kwargs,
    ):
        self.start_node: Node = (
            start_node
            if isinstance(start_node, Node)
            else Node(lambda *args, **kwargs: None, name="start")
            if start_node is None
            else Node(start_node, name="start")
        )
        self.end_node: Node = (
            end_node
            if isinstance(end_node, Node)
            else Node(lambda *args, **kwargs: None, name="end")
            if end_node is None
            else Node(end_node, name="end")
        )
        self.name = validate_name(name) if name else f"flow:{rand_str()}"

        self.node_pool: Dict[uuid.UUID, Node] = {
            self.start_node.id: self.start_node,
            self.end_node.id: self.end_node,
        }

    def run(self, *args, **kwargs) -> "FlowRunResult":
        result = {}
        node = self.start_node
        while node:
            collected_params = collect_params(
                node.func_params, *args, kwargs=result, **kwargs
            )
            self.log(
                f"Running node '{node.name}' with args: {collected_params[0]}, "
                + f"kwargs: {collected_params[1]}",
                level="debug",
            )

            _node_result = node.run(*collected_params[0], **collected_params[1])
            if isinstance(node.return_envelope, Text):
                result[node.return_envelope] = _node_result
            elif node.return_envelope is False:
                if able_to_dict(_node_result):
                    result.update(dict(_node_result))
                else:
                    self.log(
                        f"Node '{node.name}' returned a non-dict object: {_node_result} "
                        + "but set to return_envelope=False.",
                        level="warning",
                    )
            else:
                result[node.name] = _node_result

            node = node.next_[0] if node.next_ else None

        return result

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
            node.add_next(dst)
            self.node_pool[dst.id] = dst
        return node

    def log(self, msg: Text, level: Text = "debug"):
        try:
            console.print(msg[:512])
        except Exception:
            pass
