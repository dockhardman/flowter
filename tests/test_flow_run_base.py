from flowter import Flow, Node


def function_1(a: int, *args, b: int = 2, **kwargs):
    return a + b


def function_2(c: str, *args, d: str = "test", **kwargs) -> str:
    return c + d


def test_flow_run_base():
    flow = Flow()
    node_1 = Node(function_1)
    assert node_1 == flow.add_node(node_1, src=flow.start_node)

    node_2 = flow.add_node(function_2, src=node_1, dst=flow.end_node)
    assert node_2

    result = flow.run(1, 2, 3, b=4, c="5", d=6)
    print(result)
